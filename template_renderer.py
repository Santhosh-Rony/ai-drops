import os
import json
import datetime
import textwrap
from typing import Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
from config import Config
from logger import logger
from models import PostContent

def wrap_text_to_pixels(text: str, font, max_width: int, draw) -> str:
    """Wraps text to fit within a specific pixel width."""
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        left, top, right, bottom = draw.textbbox((0, 0), test_line, font=font)
        if (right - left) > max_width and len(current_line) > 1:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return "\n".join(lines)

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

def render_passage_in_region(draw, text: str, region: dict, font_path: str, override_y: int = None):
    """
    Renders multi-line text (passages) for Tips and Prompts.
    """
    if not region or not text:
        return
        
    x = region.get("x", 0)
    y = override_y if override_y is not None else region.get("y", 0)
    max_w = region.get("max_width", 500)
    
    color = (255, 255, 255, 255)
    stroke_color = (255, 255, 255, 25)
    
    # We lock the passage font size at 32px for excellent mobile readability.
    # This disconnects it from the JSON's min_font_size (24px) which is meant for bullet points.
    font_size = 32
    font = load_font(font_path, font_size)
    
    wrapped_text = wrap_text_to_pixels(text, font, max_w, draw)
    
    draw.multiline_text((x, y), wrapped_text, font=font, fill=color, spacing=15, stroke_width=1, stroke_fill=stroke_color)

def render_post(content: PostContent, template_path: str, region_config: dict, output_path: str, is_passage: bool = False):
    """
    Renders the post content into the given template using dynamic spacing and style overrides.
    """
    logger.info("Template rendering started with dynamic layout")
    
    try:
        with Image.open(template_path) as img:
            # Convert to RGBA to ensure alpha transparency works for drawing
            img = img.convert("RGBA")
            draw = ImageDraw.Draw(img, "RGBA")
            img_width, img_height = img.size
            
            line_y = 180 # Default line Y
            
            # 1. Render Header (Always uppercase)
            if "header" in region_config:
                header_text = content.header.upper()
                header_y = 220  # Moved slightly higher to use upper space
                region_config["header"]["max_font_size"] = 80
                region_config["header"]["min_font_size"] = 60
                render_text_in_region(draw, header_text, region_config["header"], Config.FONT_PATH, override_y=header_y)
                
                header_max_h = region_config["header"].get("max_height", 80)
                line_y = header_y + header_max_h + 10
            
            # 2. Render Dynamic Date in the top right corner (pushed to border)
            date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            date_region = {
                "x": 0,
                "y": 1715, # Positioned directly above the watermark
                "max_width": img_width,
                "align": "center",
                "max_font_size": 16,
                "min_font_size": 12
            }
            # Use Italic font for date
            render_text_in_region(draw, date_str, date_region, Config.FONT_ITALIC_PATH)
            
            # 2a. Draw a divider line exactly matching the width of the date text
            date_font = load_font(Config.FONT_ITALIC_PATH, 16)
            left, top, right, bottom = draw.textbbox((0, 0), date_str, font=date_font)
            date_text_width = right - left
            divider_y = 1740
            start_x = (img_width - date_text_width) // 2
            # Use 50 for alpha to make it transparent and subtle
            draw.line([(start_x, divider_y), (start_x + date_text_width, divider_y)], fill=(255, 255, 255, 50), width=2)
            
            watermark_str = "@Everything__about_ai"
            watermark_region = {
                "x": 0,
                "y": 1750, # Leaves the exact same physical gap from the bottom border as the date has from the top border
                "max_width": img_width,
                "align": "center",
                "max_font_size": 22, 
                "min_font_size": 16  
            }
            # Use Italic font for watermark to match the date style
            render_text_in_region(draw, watermark_str, watermark_region, Config.FONT_ITALIC_PATH)

            # 3. Dynamic Vertical Spacing for the 4 Tools
            start_y = line_y + 60
            end_y = 1580 # Expanded to give more room to 4 tools
            
            usable_height = end_y - start_y
            block_height = usable_height / 4.0 # Allocate 1/4th of the space to each tool
            
            def render_tool_block(tool_data, block_idx: int, base_y: float):
                if not tool_data:
                    return
                    
                prefix = f"tool_{block_idx}"
                
                # If this tool (like tool_4) is not explicitly defined in the template JSON, 
                # fallback to using tool_1's horizontal coordinates and bounds.
                if f"{prefix}_name" not in region_config:
                    prefix = "tool_1"
                
                # Dynamically set premium typography font sizes
                if f"{prefix}_name" in region_config:
                    region_config[f"{prefix}_name"]["max_font_size"] = 50
                    region_config[f"{prefix}_name"]["min_font_size"] = 40
                
                for pt_idx in range(1, 4):
                    pt_key = f"{prefix}_point_{pt_idx}"
                    if pt_key in region_config:
                        region_config[pt_key]["max_font_size"] = 32
                        region_config[pt_key]["min_font_size"] = 26
                
                # Render Block Title (Tool Name or # Tip 1)
                render_text_in_region(draw, tool_data.title, region_config[f"{prefix}_name"], Config.FONT_PATH, override_y=int(base_y), force_title=True)
                
                if is_passage:
                    # Render passage
                    passage_y = int(base_y) + 85
                    passage_region = region_config[f"{prefix}_point_1"]
                    render_passage_in_region(draw, tool_data.passage, passage_region, Config.FONT_PATH, override_y=passage_y)
                else:
                    # Render Bullet Points with much tighter vertical grouping to prevent 4-tool overlap
                    bullet_spacing = 50
                    bullet_y = int(base_y) + 90
                    
                    if tool_data.point_1:
                        formatted_point = tool_data.point_1.capitalize()
                        render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_1"], Config.FONT_PATH, override_y=bullet_y)
                    
                    bullet_y += bullet_spacing
                    if tool_data.point_2:
                        formatted_point = tool_data.point_2.capitalize()
                        render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_2"], Config.FONT_PATH, override_y=bullet_y)
                    
                    bullet_y += bullet_spacing
                    if tool_data.point_3:
                        formatted_point = tool_data.point_3.capitalize()
                        render_text_in_region(draw, f"• {formatted_point}", region_config[f"{prefix}_point_3"], Config.FONT_PATH, override_y=bullet_y)

            # Render the 4 tool blocks dynamically spaced out
            render_tool_block(content.tool_1, 1, start_y)
            render_tool_block(content.tool_2, 2, start_y + block_height)
            render_tool_block(content.tool_3, 3, start_y + (block_height * 2))
            render_tool_block(content.tool_4, 4, start_y + (block_height * 3))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Convert back to RGB if saving as JPEG, but we use PNG which supports RGBA
            img.save(output_path, "PNG", quality=95)
            logger.info("Template rendering completed successfully with dynamic spacing")
            
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise
