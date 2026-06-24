import os
import sys
import json
from logger import logger
from config import Config
from ai_content_generator import generate_ai_content
from template_renderer import get_template_for_day, render_post
from image_uploader import upload_image

def main():
    """
    Step 1: Content Generation & Image Rendering
    This script is completely decoupled from Instagram publishing and Git operations.
    """
    try:
        logger.info("Starting Step 1: AI Content Generation & Image Rendering")
        
        # 1. Validate Environment variables
        Config.validate()
        
        # 2. Discover & Generate Content using OpenAI (Strict JSON structure via prompt.py)
        post_content = generate_ai_content()
        
        # 3. Select the correct background template based on the day of the week
        template_path, region_config = get_template_for_day()
        logger.info(f"Selected template: {template_path}")
        
        # 4. Render the Image using Pillow (Text-overlay only. No AI image generation)
        output_filename = "daily_ai_drop.png"
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
