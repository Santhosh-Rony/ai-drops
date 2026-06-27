def get_ai_drops_prompt(excluded_tools: list[str] = None) -> str:
    exclusion_text = ""
    if excluded_tools:
        exclusion_text = "\n\nCRITICAL RULE: DO NOT include any of the following tools, as they have already been covered recently:\n"
        for tool in excluded_tools:
            exclusion_text += f"- {tool}\n"
            
    return f"""Search the web for the 3 most interesting AI tools, AI product launches, or major AI updates released within the last 24-48 hours.

Search Strategy:
1. FIRST, do a targeted web search on the 15 most anticipated and trending AI companies to see if they released any new AI tools, products, models, agents, chatbots, or Apps in the last 24-48 hours.
The 15 priority companies are: OpenAI, Google DeepMind, Anthropic, Microsoft, NVIDIA, Meta, xAI, Amazon, Perplexity AI, Mistral AI, DeepSeek, Apple, Scale AI, Databricks, Hugging Face.
2. If you find fewer than 3 major releases from these top 15 companies, then expand your search horizontally to include ANY major AI developments from other startups or organizations, such as:
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
        "title": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    }},
    "tool_2": {{
        "title": "Tool Name Here",
        "point_1": "Usage / Benefit 1 here",
        "point_2": "Usage / Benefit 2 here",
        "point_3": "Usage / Benefit 3 here"
    }},
    "tool_3": {{
        "title": "Tool Name Here",
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

def get_ai_tips_prompt(core_idea: str) -> str:
    return f"""You are an expert AI educator. Your task is to generate exactly 3 highly actionable, unique, and valuable AI Tips based entirely on the following core idea:

Core Idea for Today: "{core_idea}"

Return ONLY valid JSON.

Format:
{{
    "header": "AI TIPS",
    "tool_1": {{
        "title": "# Tip 1",
        "passage": "Write a clear, easy-to-understand 360-character tip here."
    }},
    "tool_2": {{
        "title": "# Tip 2",
        "passage": "Write the second 360-character tip here."
    }},
    "tool_3": {{
        "title": "# Tip 3",
        "passage": "Write the third 360-character tip here."
    }},
    "caption": "Write an engaging Instagram caption about {core_idea}...",
    "hashtags": "#aitips #ai #artificialintelligence #productivity"
}}

Rules:
* You MUST provide exactly 3 tips related to the core idea.
* The titles MUST literally be '# Tip 1', '# Tip 2', and '# Tip 3'.
* Each tip must be provided as a single passage of text (maximum 360 characters). Do NOT use bullet points. Make it a fluid, easy-to-understand paragraph.
* Header must ALWAYS be exactly 'AI TIPS'.
* The language MUST be extremely simple, beginner-friendly, and easy for anyone to understand. Avoid complex jargon.
* JSON only. No markdown formatting blocks. No extra text.
"""

def get_ai_prompts_prompt(core_idea: str) -> str:
    return f"""You are a master prompt engineer. Your task is to generate exactly 3 highly effective, ready-to-use AI Prompts based entirely on the following core idea:

Core Idea for Today: "{core_idea}"

Return ONLY valid JSON.

Format:
{{
    "header": "AI PROMPTS",
    "tool_1": {{
        "title": "# Prompt 1",
        "passage": "Write a highly effective, ready-to-copy AI prompt here (max 360 characters)."
    }},
    "tool_2": {{
        "title": "# Prompt 2",
        "passage": "Write the second 360-character prompt here."
    }},
    "tool_3": {{
        "title": "# Prompt 3",
        "passage": "Write the third 360-character prompt here."
    }},
    "caption": "Write an engaging Instagram caption about AI prompts for {core_idea}...",
    "hashtags": "#aiprompts #promptengineering #ai #chatgpt"
}}

Rules:
* You MUST provide exactly 3 distinct AI prompts related to the core idea.
* The titles MUST literally be '# Prompt 1', '# Prompt 2', and '# Prompt 3'.
* Each prompt must be a single passage of text (maximum 360 characters). It should be a direct prompt the user can copy and paste into an AI.
* Header must ALWAYS be exactly 'AI PROMPTS'.
* The language MUST be extremely simple, beginner-friendly, and easy for anyone to understand. Avoid complex jargon.
* JSON only. No markdown formatting blocks. No extra text.
"""

SYSTEM_PROMPT = """
You are a helpful AI assistant.

Your job is to follow the user's task and create accurate, practical, beginner-friendly content.

Use simple, plain English.
Keep sentences short and easy to read.
Explain ideas as if teaching someone new to AI.
Every sentence should teach something useful.
Prefer teaching over describing.
Explain why something matters or how it can be used.
Give practical advice whenever possible.
Avoid unnecessary jargon.
If a technical term is required, explain it simply.
Avoid marketing or exaggerated language.
Write naturally and conversationally.

When multiple good answers are possible, choose the one that is more practical, more useful, and easier for beginners to understand.

Follow the user's JSON schema exactly.
Return only valid JSON.
Do not output markdown.
Do not output explanations or extra text.
"""