from PIL import Image, ImageDraw, ImageFont
import os

def create_story_template():
    width, height = 1080, 1920
    
    # Dark blue/black solid background
    bg_color = (15, 23, 42, 255) # slate-900 with full opacity
    img = Image.new("RGBA", (width, height), bg_color)
    
    # Create an overlay image for transparent drawing
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Try to load a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 110)
        # Using Georgia Italic which beautifully mirrors Cardo's serif elegance
        text_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Italic.ttf", 65)
        watermark_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 35)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()
        
    # Title (Centered, Pure White)
    title = "EVERYTHING ABOUT AI\nIS LIVE"
    draw.text((width//2, height//2 - 100), title, font=title_font, fill=(255, 255, 255, 255), anchor="mm", align="center")
    
    # Body (Centered just below title, Transparent Gray)
    body = "Check the Link in our Bio\nto get them for free!"
    # Transparent Gray (R, G, B, Alpha)
    draw.text((width//2, height//2 + 100), body, font=text_font, fill=(180, 180, 180, 160), anchor="mm", align="center")
    
    # Watermark (Pushed all the way to the bottom)
    watermark_str = "@Everything__about_ai"
    draw.text((width//2, height - 100), watermark_str, font=watermark_font, fill=(148, 163, 184, 255), anchor="mm")
    
    # Composite the text layer over the background
    final_img = Image.alpha_composite(img, txt_layer)
    # Convert back to RGB for saving as PNG without massive file size if desired, but PNG supports RGBA
    
    # Save
    os.makedirs("docs", exist_ok=True)
    final_img.save("docs/story_bg.png")
    print("Story template successfully regenerated to docs/story_bg.png")

if __name__ == "__main__":
    create_story_template()
