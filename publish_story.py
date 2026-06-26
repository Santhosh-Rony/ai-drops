import os
import sys
from logger import logger
from config import Config
from instagram_publisher import publish_story

def main():
    """
    Publishes the static vertical Story image to Instagram.
    This script is designed to be executed via GitHub Actions daily at 9:00 AM.
    """
    try:
        logger.info("Starting Instagram Story Publishing")
        
        # 1. Validate Environment variables
        Config.validate()
        
        # 2. Define the static public URL of the story image
        # Because we changed the GitHub Pages root to /docs, the URL is just /story_bg.png
        image_url = f"https://{Config.GITHUB_USERNAME}.github.io/{Config.GITHUB_REPOSITORY}/story_bg.png"
        logger.info(f"Using Story Image URL: {image_url}")
        
        # 3. Publish Story to Instagram
        post_id = publish_story(image_url)
        
        logger.info(f"Successfully published Instagram Story with ID: {post_id}")
        
    except Exception as e:
        logger.error(f"Story publishing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
