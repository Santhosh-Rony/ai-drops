import json
from openai import OpenAI
from prompt import AI_DROPS_PROMPT, SYSTEM_PROMPT

def test_openrouter():
    print("=== OpenRouter API Web Search Tester ===\n")
    
    # 1. Get API Key and Model
    api_key = input("Enter your OpenRouter API Key: ").strip()
    if not api_key:
        print("API Key is required!")
        return

    print("\nRecommended Models for Web Search:")
    print(" 1. openai/gpt-oss-120b:free (Free - Requires OpenRouter Web Plugin)")
    print(" 2. qwen/qwen3-next-80b-a3b-instruct:free (Free - Requires OpenRouter Web Plugin)")
    print(" 3. perplexity/llama-3.1-sonar-huge-128k-online (Paid - Native live web search)")
    
    model_name = input("\nEnter the model name (Press Enter to default to openai/gpt-oss-120b:free): ").strip()
    if not model_name:
        model_name = "openai/gpt-oss-120b:free"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://aidrops.local",
            "X-Title": "AI Drops Automation",
        }
    )

    print(f"\nSending request to OpenRouter using model: {model_name}...")
    print("Please wait, web search might take a few seconds...\n")

    # To fix Issue 1 (No search tool attached):
    # We pass the OpenRouter Web Plugin via extra_body for generic models.
    # Perplexity models ignore this as they have native search.
    extra_body = {
        "plugins": [
            {"id": "web", "max_results": 5}
        ]
    }

    try:
        try:
            # First attempt: Try with JSON enforcement
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": AI_DROPS_PROMPT}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                extra_body=extra_body
            )
        except Exception as e:
            # To fix Issue 2 (Conflicts with response_format):
            if "json" in str(e).lower() or "format" in str(e).lower():
                print("⚠️  Model rejected strict JSON mode. Retrying without 'response_format'...")
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": AI_DROPS_PROMPT}
                    ],
                    temperature=0.7,
                    extra_body=extra_body
                )
            else:
                raise e

        content_text = response.choices[0].message.content
        
        print("\n=== RAW RESPONSE FROM MODEL ===")
        print(content_text)
        print("===============================\n")

        # 3. Robust JSON Parsing (Fixing Issue 2 & 3 where models emit text like "[Searching]" before JSON)
        try:
            # Find the first '{' and the last '}' to ignore any prefix/suffix conversational text
            start_idx = content_text.find('{')
            end_idx = content_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_string = content_text[start_idx:end_idx+1]
                parsed_json = json.loads(json_string)
                print("✅ SUCCESS: Extracted and parsed valid JSON!")
                print(json.dumps(parsed_json, indent=4))
            else:
                raise ValueError("No JSON object '{...}' found in the response.")
                
        except json.JSONDecodeError:
            print("❌ ERROR: Could not parse JSON from the response.")
            print("The model failed to format the output correctly.")

    except Exception as e:
        print(f"\n❌ Fatal API Error: {e}")

if __name__ == "__main__":
    test_openrouter()
