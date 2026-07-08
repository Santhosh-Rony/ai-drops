import json
from openai import OpenAI
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from logger import logger
from models import PostContent
from prompt import SYSTEM_PROMPT

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _generate_with_gemini(dynamic_prompt: str, is_passage: bool) -> PostContent:
    logger.info("GEMINI_API_KEY found. Attempting generation with Gemini...")
    client = genai.Client(api_key=Config.GEMINI_API_KEY)
    
    gemini_schema = {
        "type": "OBJECT",
        "properties": {
            "header": {"type": "STRING"},
            "tool_1": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "point_1": {"type": "STRING"},
                    "point_2": {"type": "STRING"},
                    "point_3": {"type": "STRING"},
                    "passage": {"type": "STRING"}
                }
            },
            "tool_2": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "point_1": {"type": "STRING"},
                    "point_2": {"type": "STRING"},
                    "point_3": {"type": "STRING"},
                    "passage": {"type": "STRING"}
                }
            },
            "tool_3": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "point_1": {"type": "STRING"},
                    "point_2": {"type": "STRING"},
                    "point_3": {"type": "STRING"},
                    "passage": {"type": "STRING"}
                }
            },
            "caption": {"type": "STRING"},
            "hashtags": {"type": "STRING"}
        },
        "required": ["header", "tool_1", "tool_2", "tool_3", "caption", "hashtags"]
    }
    
    # Prepend SYSTEM_PROMPT to the prompt since Gemini has strict roles
    full_prompt = f"SYSTEM INSTRUCTIONS:\n{SYSTEM_PROMPT}\n\nUSER REQUEST:\n{dynamic_prompt}"
    
    # Enable Google Search grounding specifically for AI Drops (is_passage=False)
    tools = [{"google_search": {}}] if not is_passage else None
    
    config_kwargs = {
        "temperature": 0.7,
        "tools": tools,
    }
    
    # Gemini API does not allow response_mime_type alongside tools
    if not tools:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = gemini_schema
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(**config_kwargs)
        )
        
        content_text = response.text
        if not content_text:
            raise ValueError("Empty text content from Gemini.")
            
        # Robust JSON Parsing to ignore markdown or tool outputs
        start_idx = content_text.find('{')
        end_idx = content_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_string = content_text[start_idx:end_idx+1]
            data = json.loads(json_string)
        else:
            raise ValueError("No JSON object '{...}' found in the Gemini response.")
            
        post_content = PostContent.from_dict(data)
        
        post_content.trim_to_limits(is_passage)
        post_content.validate(is_passage)
        
        logger.info("Content generation completed successfully using Gemini.")
        return post_content
    except Exception as e:
        logger.warning(f"Failed to generate content with Gemini. Error: {e}")
        raise

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
            "qwen/qwen3-next-80b-a3b-instruct:free",
            "google/gemma-4-31b-it:free"
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

            if not response or not hasattr(response, "choices") or not response.choices:
                raise ValueError(f"OpenRouter returned an empty or invalid response object for {model_name}.")
                
            content_text = response.choices[0].message.content
            if not content_text:
                raise ValueError("Empty text content from OpenRouter.")

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
    Loops through all available API keys in order. If one fails completely (exhausts 3 retries),
    it pivots to the next one in the daisy-chain.
    """
    api_keys = [
        Config.OPENROUTER_API_KEY,
        Config.OPENROUTER_FALLBACK_API_KEY,
        Config.OPENROUTER_FALLBACK_API_KEY_1,
        Config.OPENROUTER_FALLBACK_API_KEY_2,
        Config.OPENROUTER_FALLBACK_API_KEY_3
    ]
    
    # Filter out empty keys
    valid_keys = [k for k in api_keys if k and k.strip()]
    
    if not valid_keys:
        logger.error("No valid OpenRouter API keys found in .env!")
        raise RuntimeError("Missing API keys.")
        
    logger.info(f"Starting AI content generation pipeline. Loaded {len(valid_keys)} active API keys.")
    
    # Try Gemini First
    if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY.strip():
        try:
            return _generate_with_gemini(dynamic_prompt, is_passage)
        except Exception as e:
            logger.error(f"🔥 FATAL FAILURE on Gemini: {e}")
            logger.info("Pivoting to fallback OpenRouter API keys...")
    else:
        logger.info("GEMINI_API_KEY not found. Defaulting to OpenRouter...")
        
    last_error = None
    for idx, key in enumerate(valid_keys):
        key_label = f"Key #{idx+1}"
        logger.info(f"Attempting content generation using {key_label}...")
        try:
            return _generate_with_key(key, dynamic_prompt, is_passage)
        except Exception as e:
            logger.error(f"🔥 FATAL FAILURE on {key_label}: {e}")
            last_error = e
            if idx < len(valid_keys) - 1:
                logger.info(f"Pivoting to next fallback API key ({idx+2})...")
            continue
            
    logger.error("All available API keys have been exhausted! Script is completely locked out.")
    raise RuntimeError(f"Total failure across all {len(valid_keys)} possible API keys.") from last_error
