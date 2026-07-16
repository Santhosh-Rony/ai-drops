import time
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from logger import logger

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def create_media_container(video_url: str, caption: str, business_id: str, access_token: str) -> str:
    """
    Step 1 of Graph API: Create a media container from a video URL for REELS.
    """
    logger.info("Instagram upload started (Creating Media Container)")
    url = f"https://graph.instagram.com/v25.0/{business_id}/media"
    
    params = {
        "video_url": video_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": access_token
    }
    
    response: Optional[requests.Response] = None
    try:
        response = requests.post(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to create media container. Error: {e}")
        if response is not None:
            logger.error(f"Instagram API Response: {response.text}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def publish_post(container_id: str, business_id: str, access_token: str) -> str:
    """
    Step 2 of Graph API: Publish the created media container to the feed.
    """
    logger.info(f"Publishing media container {container_id}")
    url = f"https://graph.instagram.com/v25.0/{business_id}/media_publish"
    
    params = {
        "creation_id": container_id,
        "access_token": access_token
    }
    
    response: Optional[requests.Response] = None
    try:
        response = requests.post(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to publish media. Error: {e}")
        if response is not None:
            logger.error(f"Instagram API Response: {response.text}")
        raise

def publish_media(video_url: str, caption: str) -> str:
    """
    Orchestrates the two-step Instagram publishing process.
    """
    # Protect against AI hallucinating endless hashtags and exceeding Instagram's 2200 char limit
    if len(caption) > 2100:
        logger.warning(f"Caption length ({len(caption)}) exceeds safe limits. Truncating to 2100 chars.")
        caption = caption[:2100] + "..."
    access_token = Config.INSTAGRAM_ACCESS_TOKEN
    business_id = Config.INSTAGRAM_BUSINESS_ID
    
    if not access_token or not business_id:
        raise ValueError("Instagram credentials missing. Cannot publish.")
        
    container_id = create_media_container(video_url, caption, business_id, access_token)
    if not container_id:
        raise RuntimeError("Failed to retrieve a valid container_id from Instagram API")
        
    logger.info(f"Created media container with ID: {container_id}")
    
    # Wait for Instagram to process the image container before publishing
    time.sleep(5)
    
    post_id = publish_post(container_id, business_id, access_token)
    logger.info("Instagram publish completed")
    return post_id

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def create_story_media_container(image_url: str, business_id: str, access_token: str) -> str:
    """
    Create a media container for a STORY from an image URL.
    Stories cannot have captions via the API.
    """
    logger.info("Instagram Story upload started (Creating Media Container)")
    url = f"https://graph.instagram.com/v25.0/{business_id}/media"
    
    params = {
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": access_token
    }
    
    response: Optional[requests.Response] = None
    try:
        response = requests.post(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to create story media container. Error: {e}")
        if response is not None:
            logger.error(f"Instagram API Response: {response.text}")
        raise

def publish_story(image_url: str) -> str:
    """
    Orchestrates the two-step Instagram publishing process for a STORY.
    """
    access_token = Config.INSTAGRAM_ACCESS_TOKEN
    business_id = Config.INSTAGRAM_BUSINESS_ID
    
    if not access_token or not business_id:
        raise ValueError("Instagram credentials missing. Cannot publish story.")
        
    container_id = create_story_media_container(image_url, business_id, access_token)
    if not container_id:
        raise RuntimeError("Failed to retrieve a valid container_id for Story from Instagram API")
        
    logger.info(f"Created story media container with ID: {container_id}")
    
    # Wait for Instagram to process the image container before publishing
    time.sleep(5)
    
    post_id = publish_post(container_id, business_id, access_token)
    logger.info("Instagram Story publish completed")
    return post_id

