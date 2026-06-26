import os
import json
import datetime
from config import Config
from logger import logger
from models import PostContent

# We store databases in docs/ so the GitHub Pages frontend can fetch them freely
DB_DROPS = os.path.join("docs", "db_drops.json")
DB_TIPS = os.path.join("docs", "db_tips.json")
DB_PROMPTS = os.path.join("docs", "db_prompts.json")

def load_db(file_path: str) -> list:
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not read {file_path}, starting fresh. Error: {e}")
        return []

def save_db(file_path: str, data: list):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Successfully saved {len(data)} records to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save to {file_path}: {e}")

def save_to_database(post_content: PostContent, post_type: str):
    """
    Saves the generated AI content into the JSON database for the Web App.
    """
    logger.info(f"Saving {post_type} content to Web App Database...")
    
    timestamp = datetime.datetime.now().strftime("%B %d, %Y")
    
    if post_type == "drops":
        db_path = DB_DROPS
        new_entry = {
            "date": timestamp,
            "items": [
                {
                    "title": post_content.tool_1.title,
                    "description": post_content.tool_1.description
                },
                {
                    "title": post_content.tool_2.title,
                    "description": post_content.tool_2.description
                },
                {
                    "title": post_content.tool_3.title,
                    "description": post_content.tool_3.description
                }
            ]
        }
    elif post_type in ["tips", "prompts"]:
        db_path = DB_TIPS if post_type == "tips" else DB_PROMPTS
        new_entry = {
            "date": timestamp,
            "title": post_content.passage_title,
            "content": post_content.passage_content
        }
    else:
        logger.warning(f"Unknown post_type for database: {post_type}")
        return

    data = load_db(db_path)
    data.insert(0, new_entry) # Add to the top of the feed
    
    # Keep the last 100 entries
    if len(data) > 100:
        data = data[:100]
        
    save_db(db_path, data)
