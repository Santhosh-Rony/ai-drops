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
    day_name_lower = days[today_index].lower()
    day_name_capital = days[today_index]
    
    # Try lowercase first (standardized)
    template_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name_lower}.png")
    json_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name_lower}.json")
    
    if not os.path.exists(template_path) or not os.path.exists(json_path):
        # Fallback to Capitalized (in case Linux server has original casing)
        template_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name_capital}.png")
        json_path = os.path.join(Config.TEMPLATES_DIR, f"{day_name_capital}.json")
        
    if not os.path.exists(template_path) or not os.path.exists(json_path):
        logger.warning(f"Template files for {day_name_capital} not found. Searching for fallback templates.")
        for fallback_day in days:
            for case_format in [fallback_day.lower(), fallback_day]:
                fallback_img = os.path.join(Config.TEMPLATES_DIR, f"{case_format}.png")
                fallback_json = os.path.join(Config.TEMPLATES_DIR, f"{case_format}.json")
                if os.path.exists(fallback_img) and os.path.exists(fallback_json):
                    logger.info(f"Using fallback template: {case_format}")
                    template_path = fallback_img
                    json_path = fallback_json
                    break
            if os.path.exists(template_path):
                break
        else:
            raise FileNotFoundError(f"No valid template sets found in {Config.TEMPLATES_DIR}.")
            
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

def render_text_in_region(draw, text: str, region: dict, font_path: str, override_y: int = None, force_upper: bool = False, force_title: bool = False, force_sentence: bool = False):
    """
    Renders text inside a defined region with auto-sizing to fit max_width.
    """
    if not region or not text:
        return
        
    if force_upper:
        text = text.upper()
    if force_title:
        text = text.title()
    if force_sentence:
        text = text.capitalize()
        
    x = region.get("x", 0)
    y = override_y if override_y is not None else region.get("y", 0)
    max_w = region.get("max_width", 500)
    align = region.get("align", "left")
    
    # Enforce ALL text to be Pure Opaque White
    color = (255, 255, 255, 255)
    
    # Use a whisper-thin transparent stroke to give structure without making it bold
    stroke_color = (255, 255, 255, 25)
    
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
        
    # Draw main text in pure white with a whisper-thin stroke to maintain crispness
    draw.text((draw_x, y), text, font=font, fill=color, stroke_width=1, stroke_fill=stroke_color)

def render_post(content: PostContent, template_path: str, region_config: dict, output_path: str):
    """
    Renders the post content into the given template using dynamic spacing and style overrides.
    """
    logger.info("Template rendering started with dynamic layout")
    
    try:
        with Image.open(template_path) as img:
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size
            
            line_y = 180 # Default line Y
            
            # 1. Render Header (Always uppercase)
            if "header" in region_config:
                header_text = content.header.upper()
                render_text_in_region(draw, header_text, region_config["header"], Config.FONT_PATH)
                
                header_y = region_config["header"].get("y", 80)
                header_max_h = region_config["header"].get("max_height", 100)
                line_y = header_y + header_max_h + 10
            
            # 2. Render Dynamic Date in the top right corner (pushed to border)
            date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            date_region = {
                "x": img_width - 60 - 400, # Tighter right padding
                "y": 60, # Moved down slightly
                "max_width": 400,
                "align": "right",
                "max_font_size": 16, # Reduced from 25
                "min_font_size": 12  # Reduced from 18
            }
            # Use Italic font for date
            render_text_in_region(draw, date_str, date_region, Config.FONT_ITALIC_PATH)
            
            # 2b. Render Watermark in the bottom right corner
            watermark_str = "@Everything__about_ai"
            watermark_region = {
                "x": img_width - 60 - 400, # Same right padding as the date
                "y": img_height - 60 - 30, # Pushed down to the bottom border
                "max_width": 400,
                "align": "right",
                "max_font_size": 16, 
                "min_font_size": 12  
            }
            # Use Italic font for watermark to match the date style
            render_text_in_region(draw, watermark_str, watermark_region, Config.FONT_ITALIC_PATH)

            # 3. Dynamic Vertical Spacing for the 3 Tools
            start_y = line_y + 60
            end_y = img_height - 150 # Leave padding at the bottom
            
            usable_height = end_y - start_y
            block_height = usable_height / 3.0 # Allocate 1/3rd of the space to each tool
            
            def render_tool_block(tool_data, block_idx: int, base_y: float):
                prefix = f"tool_{block_idx}"
                
                # Render Tool Name (Title Case: First Letter Capital of Every Word)
                render_text_in_region(draw, tool_data.name, region_config[f"{prefix}_name"], Config.FONT_PATH, override_y=int(base_y), force_title=True)
                
                # Render Bullet Points (Sentence Case: First starting letter capital only)
                bullet_y = int(base_y) + 85
                if tool_data.point_1:
                    formatted_point = tool_data.point_1.capitalize()
                    render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_1"], Config.FONT_PATH, override_y=bullet_y)
                
                bullet_y += 65
                if tool_data.point_2:
                    formatted_point = tool_data.point_2.capitalize()
                    render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_2"], Config.FONT_PATH, override_y=bullet_y)
                
                bullet_y += 65
                if tool_data.point_3:
                    formatted_point = tool_data.point_3.capitalize()
                    render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_3"], Config.FONT_PATH, override_y=bullet_y)

            # Render the 3 tool blocks dynamically spaced out
            render_tool_block(content.tool_1, 1, start_y)
            render_tool_block(content.tool_2, 2, start_y + block_height)
            render_tool_block(content.tool_3, 3, start_y + (block_height * 2))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PNG", quality=95)
            logger.info("Template rendering completed successfully with dynamic spacing")
            
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise
