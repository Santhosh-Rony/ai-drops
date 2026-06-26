from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request
import datetime

def get_bubble_font(size):
    font_path = "fonts/Chewy-Regular.ttf"
    if not os.path.exists(font_path):
        os.makedirs("fonts", exist_ok=True)
        url = "https://github.com/google/fonts/raw/main/apache/chewy/Chewy-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            print(f"Failed to download bubble font: {e}")
            return ImageFont.load_default()
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def get_best_font(mac_path, linux_path, size):
    if os.path.exists(mac_path):
        return ImageFont.truetype(mac_path, size)
    if os.path.exists(linux_path):
        return ImageFont.truetype(linux_path, size)
    
    # Ultimate Fallback: The Cardo font we already use for the main posts
    fallback_cardo = "fonts/Cardo-Bold.ttf"
    if os.path.exists(fallback_cardo):
        return ImageFont.truetype(fallback_cardo, size)
        
    return ImageFont.load_default()

def create_story_template():
    width, height = 1080, 1920
    
    # Load fonts using robust multi-platform fallbacks
    title_font = get_best_font(
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
        110
    )
    text_font = get_best_font(
        "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        65
    )
    watermark_font = get_best_font(
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        35
    )
        
    bubble_font = get_bubble_font(120)
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    os.makedirs("docs", exist_ok=True)
    
    for day_of_week in days_of_week:
        # Dark blue/black solid background
        bg_color = (15, 23, 42, 255) # slate-900 with full opacity
        img = Image.new("RGBA", (width, height), bg_color)
        
        # Create an overlay image for transparent drawing
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # 1. Day of the Week (Rainbow Bubble Font)
        greeting = f"Hi, I'm {day_of_week}"
        
        # Calculate width of greeting to center it
        total_width = draw.textlength(greeting, font=bubble_font)
        start_x = (width - total_width) / 2
        y_pos = height//2 - 400
        
        # Bright Playful Colors
        rainbow = [(255, 89, 94, 255), (255, 202, 58, 255), (138, 201, 38, 255), (25, 130, 196, 255), (106, 76, 147, 255)]
        current_x = start_x
        for i, char in enumerate(greeting):
            color = rainbow[i % len(rainbow)] if char != " " else (0,0,0,0)
            draw.text((current_x, y_pos), char, font=bubble_font, fill=color)
            current_x += draw.textlength(char, font=bubble_font)
            
        # 2. Title (Centered, Pure White)
        title = "EVERYTHING ABOUT AI\nIS LIVE"
        draw.text((width//2, height//2 - 100), title, font=title_font, fill=(255, 255, 255, 255), anchor="mm", align="center")
        
        # 3. Body (Centered just below title, Transparent Gray)
        body = "Check the Link in our Bio\nto get them for free!"
        draw.text((width//2, height//2 + 100), body, font=text_font, fill=(180, 180, 180, 160), anchor="mm", align="center")
        
        # 4. Watermark (Pushed all the way to the bottom)
        watermark_str = "@Everything__about_ai"
        draw.text((width//2, height - 100), watermark_str, font=watermark_font, fill=(148, 163, 184, 255), anchor="mm")
        
        # Composite the text layer over the background
        final_img = Image.alpha_composite(img, txt_layer)
        
        # Save securely using lower-case naming for Linux safety
        file_name = f"docs/story_template_{day_of_week.lower()}.png"
        final_img.save(file_name)
        print(f"Generated: {file_name}")

if __name__ == "__main__":
    create_story_template()
