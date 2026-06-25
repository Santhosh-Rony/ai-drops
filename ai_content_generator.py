import json
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from logger import logger
from models import PostContent
from prompt import SYSTEM_PROMPT

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _generate_with_key(api_key: str, dynamic_prompt: str, is_passage: bool) -> PostContent:
    """
    Calls OpenRouter to generate the AI drops content with retries.
    It implements a fallback mechanism across multiple free models.
    """
    logger.info("Content generation attempt started")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://aidrops.local",
            "X-Title": "AI Drops Automation",
        }
    )

    # Models to try in order of preference depending on content type
    if is_passage:
        models_to_try = [
            "openai/gpt-oss-120b:free",
            "google/gemma-4-31b-it:free",
            "qwen/qwen3-next-80b-a3b-instruct:free"    
        ]
    else:
        models_to_try = [
            "openai/gpt-oss-120b:free",
            "qwen/qwen3-next-80b-a3b-instruct:free",
            "google/gemma-4-31b-it:free"
        ]
    
    # Attach web search plugin specifically for OpenRouter generic models
    extra_body = {
        "plugins": [
            {"id": "web", "max_results": 5}
        ]
    } if not is_passage else {} # Web search is only needed for Drops, not for Tips/Prompts

    last_exception = None

    for model_name in models_to_try:
        logger.info(f"Attempting content generation using model: {model_name}")
        try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": dynamic_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    extra_body=extra_body
                )
            except Exception as e:
                if "json" in str(e).lower() or "format" in str(e).lower():
                    logger.warning(f"Model {model_name} rejected strict JSON mode. Retrying without 'response_format'...")
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": dynamic_prompt}
                        ],
                        temperature=0.7,
                        extra_body=extra_body
                    )
                else:
                    raise e

            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("Empty response from OpenRouter")

            logger.debug(f"OpenRouter raw response from {model_name}: {content_text}")
            
            # Robust JSON Parsing to ignore tool log outputs like [Searching]
            start_idx = content_text.find('{')
            end_idx = content_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_string = content_text[start_idx:end_idx+1]
                data = json.loads(json_string)
            else:
                raise ValueError("No JSON object '{...}' found in the response.")
                
            post_content = PostContent.from_dict(data)
            
            # Apply strict length constraints
            post_content.trim_to_limits(is_passage)
            post_content.validate(is_passage)
            
            logger.info(f"Content generation completed successfully using {model_name}")
            return post_content

        except Exception as e:
            logger.warning(f"Failed to generate content with {model_name}. Error: {e}")
            last_exception = e
            continue  # Try the next model in the list

    # If the loop finishes without returning, all models have failed.
    logger.error("All model fallback options have failed for this attempt.")
    if last_exception:
        raise last_exception
    else:
        raise RuntimeError("Content generation failed across all models.")

def generate_ai_content(dynamic_prompt: str, is_passage: bool = False) -> PostContent:
    """
    Main entrypoint.
    Attempts to generate using the PRIMARY API Key (up to 3 times via @retry).
    If it completely exhausts the primary key limits, it pivots to the FALLBACK API Key.
    """
    logger.info("Starting AI content generation pipeline with PRIMARY API key.")
        
    try:
        return _generate_with_key(Config.OPENROUTER_API_KEY, dynamic_prompt, is_passage)
    except Exception as primary_error:
        logger.error(f"PRIMARY API Key exhausted all 3 attempts! Error: {primary_error}")
        
        # Check if the user has provided a fallback key in .env
        if Config.OPENROUTER_FALLBACK_API_KEY:
            logger.info("🔥 FATAL PRIMARY FAILURE: Pivoting to FALLBACK API Key...")
            try:
                return _generate_with_key(Config.OPENROUTER_FALLBACK_API_KEY, dynamic_prompt, is_passage)
            except Exception as fallback_error:
                logger.error(f"FALLBACK API Key also exhausted all attempts! Fatal Error: {fallback_error}")
                raise RuntimeError("Total failure across both Primary and Fallback API keys.") from fallback_error
        else:
            logger.error("No fallback API key configured in .env. Failsafe aborted.")
            raise RuntimeError("Primary key failed and no fallback key exists.") from primary_error
