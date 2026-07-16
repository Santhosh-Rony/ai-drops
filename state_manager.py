import os
import json
from config import Config
from logger import logger

STATE_FILE = os.path.join(Config.OUTPUT_DIR, "state.json")

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load state: {e}. Starting fresh.")
    return {"tips_index": 0, "prompts_index": 0, "music_index": 1}

def save_state(state: dict):
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

def get_next_idea_index(post_type: str, list_length: int) -> int:
    """Returns the current index and automatically increments/saves state."""
    state = load_state()
    
    if post_type == "tips":
        current_index = state.get("tips_index", 0)
        state["tips_index"] = (current_index + 1) % list_length
    elif post_type == "prompts":
        current_index = state.get("prompts_index", 0)
        state["prompts_index"] = (current_index + 1) % list_length
    else:
        return 0
        
    save_state(state)
    return current_index

def get_next_music_index(total_music_files: int = 14) -> int:
    """Returns the current music index (1-based) and automatically increments/saves state."""
    state = load_state()
    
    current_index = state.get("music_index", 1)
    
    # Boundary fallback in case state.json has corrupted data (like 0)
    if current_index < 1 or current_index > total_music_files:
        current_index = 1
    
    # Increment for next time, looping back to 1 if we exceed total
    next_index = current_index + 1
    if next_index > total_music_files:
        next_index = 1
        
    state["music_index"] = next_index
    save_state(state)
    
    return current_index
