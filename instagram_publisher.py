import time
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from logger import logger

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def create_media_container(image_url: str, caption: str, business_id: str, access_token: str) -> str:
    """
    Step 1 of Graph API: Create a media container from an image URL.
    """
    logger.info("Instagram upload started (Creating Media Container)")
    url = f"https://graph.instagram.com/v25.0/{business_id}/media"
    
    params = {
        "image_url": image_url,
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

def publish_media(image_url: str, caption: str) -> str:
    """
    Orchestrates the two-step Instagram publishing process.
    """
    access_token = Config.INSTAGRAM_ACCESS_TOKEN
    business_id = Config.INSTAGRAM_BUSINESS_ID
    
    if not access_token or not business_id:
        raise ValueError("Instagram credentials missing. Cannot publish.")
        
    container_id = create_media_container(image_url, caption, business_id, access_token)
    if not container_id:
        raise RuntimeError("Failed to retrieve a valid container_id from Instagram API")
        
    logger.info(f"Created media container with ID: {container_id}")
    
    # Wait for Instagram to process the image container before publishing
    time.sleep(5)
    
    post_id = publish_post(container_id, business_id, access_token)
    logger.info("Instagram publish completed")
    return post_id
