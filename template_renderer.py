import os
import json
import datetime
from typing import Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
from config import Config
from logger import logger
from models import PostContent

def get_template_for_day() -> Tuple[str, Dict]:
    """
    Returns the template image path and its associated JSON configuration for the current day.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today_index = datetime.datetime.now().weekday()
    day_name = days[today_index]
    
    template_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name}.png")
    json_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name}.json")
    
    if not os.path.exists(template_path) or not os.path.exists(json_path):
        logger.warning(f"Template files for {day_name} not found. Searching for fallback templates.")
        # Try any available template as fallback
        for fallback_day in days:
            fallback_img = os.path.join(Config.TEMPLATES_DIR, f"{fallback_day}.png")
            fallback_json = os.path.join(Config.TEMPLATES_DIR, f"{fallback_day}.json")
            if os.path.exists(fallback_img) and os.path.exists(fallback_json):
                logger.info(f"Using fallback template: {fallback_day}")
                template_path = fallback_img
                json_path = fallback_json
                break
        else:
            raise FileNotFoundError(f"No valid template sets (PNG + JSON) found in {Config.TEMPLATES_DIR}.")
            
    with open(json_path, 'r', encoding='utf-8') as f:
        region_config = json.load(f)
        
    return template_path, region_config

def load_font(font_path: str, size: int):
    """Loads the specified TrueType font, falling back to default if missing."""
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        logger.warning(f"Font {font_path} not found or invalid. Using Pillow default font.")
        return ImageFont.load_default()

def render_text_in_region(draw, text: str, region: dict, font_path: str):
    """
    Renders text inside a defined region with auto-sizing to fit max_width.
    """
    if not region:
        return
        
    x, y = region.get("x", 0), region.get("y", 0)
    max_w = region.get("max_width", 500)
    align = region.get("align", "left")
    color = region.get("color", "#000000")
    
    font_size = region.get("max_font_size", 40)
    min_size = region.get("min_font_size", 20)
    font = load_font(font_path, font_size)
    
    # Calculate initial text bounds
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_w = right - left
    
    # Reduce font size until it fits the max width or hits the min size
    while text_w > max_w and font_size > min_size:
        font_size -= 2
        font = load_font(font_path, font_size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_w = right - left

    # Calculate alignment x-offset
    draw_x = x
    if align == "center":
        draw_x = x + (max_w - text_w) / 2
    elif align == "right":
        draw_x = x + (max_w - text_w)
        
    draw.text((draw_x, y), text, font=font, fill=color)

def render_post(content: PostContent, template_path: str, region_config: dict, output_path: str):
    """
    Renders the post content into the given template using the provided region config.
    """
    logger.info("Template rendering started")
    
    try:
        with Image.open(template_path) as img:
            draw = ImageDraw.Draw(img)
            
            def draw_region(region_name, text):
                if region_name in region_config:
                    if text:
                        # Append bullet point for list items
                        if "_point_" in region_name:
                            text = f"• {text}"
                        render_text_in_region(draw, text, region_config[region_name], Config.FONT_PATH)
                else:
                    logger.warning(f"Region {region_name} not defined in JSON configuration.")

            draw_region("header", content.header)
            
            # Tool 1
            draw_region("tool_1_name", content.tool_1.name)
            draw_region("tool_1_point_1", content.tool_1.point_1)
            draw_region("tool_1_point_2", content.tool_1.point_2)
            draw_region("tool_1_point_3", content.tool_1.point_3)
            
            # Tool 2
            draw_region("tool_2_name", content.tool_2.name)
            draw_region("tool_2_point_1", content.tool_2.point_1)
            draw_region("tool_2_point_2", content.tool_2.point_2)
            draw_region("tool_2_point_3", content.tool_2.point_3)
            
            # Tool 3
            draw_region("tool_3_name", content.tool_3.name)
            draw_region("tool_3_point_1", content.tool_3.point_1)
            draw_region("tool_3_point_2", content.tool_3.point_2)
            draw_region("tool_3_point_3", content.tool_3.point_3)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PNG", quality=95)
            logger.info("Template rendering completed")
            
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise
