import os
import sys
import json
import glob
from logger import logger
from config import Config
from ai_content_generator import generate_ai_content
from template_renderer import get_template_for_day, render_post
from image_uploader import upload_image
from history import load_history, save_history

def cleanup_old_images():
    """
    Deletes previously generated images to prevent the repository from bloating.
    This guarantees only 1 image exists in the repo at any given time.
    """
    logger.info("Cleaning up old generated images...")
    for folder in [Config.OUTPUT_DIR, "docs"]:
        if os.path.exists(folder):
            for file_path in glob.glob(os.path.join(folder, "aidrop_*.png")):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old image: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not delete old image {file_path}: {e}")

def main():
    """
    Step 1: Content Generation & Image Rendering
    This script is completely decoupled from Instagram publishing and Git operations.
    """
    try:
        logger.info("Starting Step 1: AI Content Generation & Image Rendering")
        
        # 0. Clean up yesterday's images so they don't bloat the repository
        cleanup_old_images()
        
        # 1. Validate Environment variables
        Config.validate()
        
        # 2. Discover & Generate Content using OpenAI (Strict JSON structure via prompt.py)
        # Load history to prevent hallucinations/duplicate posts
        past_tools = load_history()
        post_content = generate_ai_content(excluded_tools=past_tools)
        
        # Save newly generated tools to history
        new_tool_names = [post_content.tool_1.name, post_content.tool_2.name, post_content.tool_3.name]
        save_history(new_tool_names)
        
        # 3. Select the correct background template based on the day of the week
        template_path, region_config = get_template_for_day()
        logger.info(f"Selected template: {template_path}")
        
        # 4. Render the Image using Pillow (Text-overlay only. No AI image generation)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"aidrop_{timestamp}.png"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        render_post(post_content, template_path, region_config, output_path)
        logger.info(f"Rendered final image locally at {output_path}")
        
        # 5. Prepare Image for GitHub Pages (Just copies to docs/ and builds expected URL string)
        image_url = upload_image(output_path)
        
        # 6. Save metadata for Step 2 (publish_instagram.py) to read later
        metadata = {
            "image_url": image_url,
            "caption": f"{post_content.caption}\n\n{post_content.hashtags}"
        }
        metadata_path = os.path.join(Config.OUTPUT_DIR, "post_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"Metadata saved to {metadata_path}. Generation complete. Awaiting GitHub Actions sync.")
        
    except Exception as e:
        logger.error(f"Application run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
