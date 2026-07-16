import os
import json
from config import Config
from logger import logger

HISTORY_FILE = os.path.join(Config.OUTPUT_DIR, "history.json")
MAX_HISTORY_ITEMS = 15 # Remembers the last 5 days (3 tools per day)

def load_history() -> list[str]:
    """
    Loads the list of previously generated AI tools from the history file.
    Returns an empty list if the file doesn't exist yet.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [t.lower().strip() for t in data.get("tools", [])]
    except Exception as e:
        logger.warning(f"Could not read history file, starting fresh. Error: {e}")
        return []

def save_history(new_tools: list[str]):
    """
    Appends newly generated tools to the history file, maintaining a rolling window.
    """
    current_history = load_history()
    
    # Add new tools to the end (normalized)
    normalized_new = [t.lower().strip() for t in new_tools]
    current_history.extend(normalized_new)
    
    # Trim to MAX_HISTORY_ITEMS (keep the most recent ones at the end of the list)
    if len(current_history) > MAX_HISTORY_ITEMS:
        current_history = current_history[-MAX_HISTORY_ITEMS:]
        
    try:
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"tools": current_history}, f, indent=4)
        logger.info(f"Saved {len(new_tools)} new tools to history. Total memory size: {len(current_history)} items.")
    except Exception as e:
        logger.error(f"Failed to save history file: {e}")
