import os
import sys
import json
import glob
from logger import logger
from config import Config
from ai_content_generator import generate_ai_content
from template_renderer import get_template_for_day, render_post
from image_uploader import upload_image
from database import save_to_database
from state_manager import get_next_idea_index
from core_ideas import AI_TIPS_IDEAS, AI_PROMPTS_IDEAS
from prompt import get_ai_drops_prompt, get_ai_tips_prompt, get_ai_prompts_prompt

def cleanup_old_images(prefix: str):
    """
    Deletes previously generated images and videos matching the current prefix to prevent repo bloat.
    """
    logger.info(f"Cleaning up old generated {prefix} media...")
    for folder in [Config.OUTPUT_DIR, "docs"]:
        if os.path.exists(folder):
            # Clean up both PNG and MP4 files
            for ext in ["png", "mp4"]:
                for file_path in glob.glob(os.path.join(folder, f"{prefix}_*.{ext}")):
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Could not delete old file {file_path}: {e}")

def main():
    """
    Step 1: Content Generation & Image Rendering
    This script is decoupled from Instagram publishing and Git operations.
    """
    try:
        logger.info("Starting Step 1: AI Content Generation & Image Rendering")
        
        # Determine Post Type (drops, tips, prompts)
        post_type = os.environ.get("POST_TYPE", "drops").lower()
        logger.info(f"Detected POST_TYPE: {post_type}")
        
        prefix = "aidrop"
        if post_type == "tips":
            prefix = "aitip"
        elif post_type == "prompts":
            prefix = "aiprompt"
        
        # 0. Clean up yesterday's images for this specific post type
        cleanup_old_images(prefix)
        
        # 1. Validate Environment variables
        Config.validate()
        
        # 2. Build the Dynamic Prompt based on POST_TYPE
        is_passage = False
        dynamic_prompt = ""
        
        if post_type == "drops":
            from core_ideas import HUMANS_VS_AI_IDEAS
            from prompt import get_humans_vs_ai_prompt
            
            is_passage = False
            
            # Fetch 2 tasks for the showdown
            idx1 = get_next_idea_index("drops", len(HUMANS_VS_AI_IDEAS), increment=1)
            idx2 = get_next_idea_index("drops", len(HUMANS_VS_AI_IDEAS), increment=1)
            
            task_1 = HUMANS_VS_AI_IDEAS[idx1]
            task_2 = HUMANS_VS_AI_IDEAS[idx2]
            logger.info(f"Selected Tasks for Humans vs AI: 1) {task_1} 2) {task_2}")
            
            dynamic_prompt = get_humans_vs_ai_prompt(task_1, task_2)
            post_content = generate_ai_content(dynamic_prompt=dynamic_prompt, is_passage=is_passage)
        elif post_type == "tips":
            is_passage = True
            idx = get_next_idea_index("tips", len(AI_TIPS_IDEAS))
            core_idea = AI_TIPS_IDEAS[idx]
            logger.info(f"Selected Core Idea for Tips (Index {idx}): {core_idea}")
            dynamic_prompt = get_ai_tips_prompt(core_idea)
            post_content = generate_ai_content(dynamic_prompt=dynamic_prompt, is_passage=is_passage)
        elif post_type == "prompts":
            is_passage = True
            idx = get_next_idea_index("prompts", len(AI_PROMPTS_IDEAS))
            core_idea = AI_PROMPTS_IDEAS[idx]
            logger.info(f"Selected Core Idea for Prompts (Index {idx}): {core_idea}")
            dynamic_prompt = get_ai_prompts_prompt(core_idea)
            post_content = generate_ai_content(dynamic_prompt=dynamic_prompt, is_passage=is_passage)
        else:
            raise ValueError(f"Unknown POST_TYPE: {post_type}")
        
        # 4. Select the correct background template based on the day of the week
        template_path, region_config = get_template_for_day()
        logger.info(f"Selected template: {template_path}")
        
        # 5. Render the Image
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
        output_filename = f"{prefix}_{timestamp}.png"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        render_post(post_content, template_path, region_config, output_path, is_passage=is_passage)
        logger.info(f"Rendered final image locally at {output_path}")
        
        # 5b. Generate Video Reel
        from state_manager import get_next_music_index
        from video_generator import generate_video
        
        music_index = get_next_music_index()
        audio_path = os.path.join("music", f"music{music_index}.mp3")
        video_output_filename = f"{prefix}_{timestamp}.mp4"
        video_output_path = os.path.join(Config.OUTPUT_DIR, video_output_filename)
        
        logger.info(f"Selected music track: {audio_path}")
        generate_video(output_path, audio_path, video_output_path, duration=10)
        
        # 6. Prepare Media for GitHub Pages
        video_url = upload_image(video_output_path)
        
        # 7. Save metadata for publish_instagram.py
        metadata = {
            "video_url": video_url,
            "caption": f"{post_content.caption}\n\n{post_content.hashtags}"
        }
        metadata_path = os.path.join(Config.OUTPUT_DIR, "post_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        # 8. Save post to the Everything About AI Web App Database
        save_to_database(post_content, post_type)
            
        logger.info(f"Metadata saved to {metadata_path}. Generation complete. Awaiting GitHub Actions sync.")
        
    except Exception as e:
        logger.error(f"Application run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
