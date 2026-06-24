# This file contains all OpenAI prompts used in the application.
# Keeping prompts here allows for easy modification without changing application logic.

AI_DROPS_PROMPT = """Search the web for the 3 most interesting AI tools, AI product launches, or major AI updates released within the last 24 hours.

Include sources such as:
- AI tool launches
- AI product launches
- AI feature releases
- OpenAI announcements
- Anthropic announcements
- Google AI announcements
- Hugging Face releases
- Product Hunt AI launches

If fewer than 3 valid AI launches are found within the last 24 hours, use notable AI launches or updates from the last 7 days.

You MUST always return exactly 3 tools. Never return fewer than 3 tools.

Return ONLY valid JSON.

Format:
{
    "header": "AI DROPS",
    "tool_1": {
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    },
    "tool_2": {
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    },
    "tool_3": {
        "name": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    },
    "caption": "Write a compelling Instagram caption here...",
    "hashtags": "#aidrops #ai #artificialintelligence"
}

Rules:
* Header must ALWAYS be exactly 'AI DROPS'. Never generate custom headlines.
* Tool name max 25 chars
* Usage/Benefit max 60 chars
* Exact structure with 3 tools is mandatory
* JSON only
* No markdown formatting tags like ```json
* No explanations
* No surrounding text"""

SYSTEM_PROMPT = "You are a helpful assistant that strictly outputs valid JSON data matching the requested schema. You use web search capabilities to find the latest announcements."
