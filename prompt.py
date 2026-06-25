# This file contains all OpenAI prompts used in the application.
# Keeping prompts here allows for easy modification without changing application logic.

def get_ai_drops_prompt(excluded_tools: list[str] = None) -> str:
    exclusion_text = ""
    if excluded_tools:
        exclusion_text = "\n\nCRITICAL RULE: DO NOT include any of the following tools, as they have already been covered recently:\n"
        for tool in excluded_tools:
            exclusion_text += f"- {tool}\n"
            
    return f"""Search the web for the 3 most interesting AI tools, AI product launches, or major AI updates released within the last 24 hours.

Search Strategy:
First, search for AI software tools released in the last 24 hours.
If there are fewer than 3 major software tools, expand your search horizontally to include ANY major AI developments:
- AI Hardware (chips, servers, devices)
- AI Infrastructure and open-source Frameworks
- AI Applications in specific domains (Healthcare, Finance, Robotics, etc.)
- Major AI research papers or open-weights model releases
As long as it is highly relevant to the AI industry and released recently, it is valid.{exclusion_text}

You MUST always return exactly 3 tools. Never return fewer than 3 tools.

Return ONLY valid JSON.

Format:
{{
    "header": "AI DROPS",
    "tool_1": {{
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    }},
    "tool_2": {{
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    }},
    "tool_3": {{
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    }},
    "caption": "Write a compelling Instagram caption here...",
    "hashtags": "#aidrops #ai #artificialintelligence"
}}

Rules:
* First, find the absolute most important AI tools released in the last 24 hours, completely ignoring character lengths during your search.
* Second, you MUST create shorter versions of the content to fit our strict design constraints without losing the core meaning:
  - Tool name: If the real tool name is larger than 25 characters, you MUST provide a shorter version of the tool name that fits under 25 characters but people can still easily understand.
  - Usage/Benefit: If the real benefit is 100-200 characters long, you MUST provide a shorter version that fits under 60 characters. Use extremely simple, plain English so anyone can understand.
* Header must ALWAYS be exactly 'AI DROPS'. Never generate custom headlines.
* Exact structure with 3 tools is mandatory
* JSON only
* No markdown formatting tags like ```json
* No explanations
* No surrounding text"""

SYSTEM_PROMPT = "You are a helpful assistant that strictly outputs valid JSON data matching the requested schema. You use web search capabilities to find the latest announcements."
