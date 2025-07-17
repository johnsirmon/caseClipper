"""
Icon generator for CaseClipSaver
Creates a simple .ico file for the system tray
"""
from PIL import Image, ImageDraw
import os


def create_icon():
    """Create application icon"""
    # Create icon sizes
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create image with transparent background
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Scale elements based on size
        margin = max(2, size // 16)
        clip_width = size - (margin * 4)
        clip_height = size - (margin * 2)
        
        # Draw clipboard base
        clipboard_color = (70, 130, 180, 255)  # Steel blue
        draw.rectangle([
            margin * 2, 
            margin * 3, 
            margin * 2 + clip_width, 
            margin * 3 + clip_height
        ], fill=clipboard_color, outline=(0, 0, 0, 255), width=max(1, size // 32))
        
        # Draw clipboard clip
        clip_size = max(4, size // 8)
        clip_x = (size - clip_size) // 2
        draw.rectangle([
            clip_x, 
            margin, 
            clip_x + clip_size, 
            margin * 3
        ], fill=clipboard_color, outline=(0, 0, 0, 255), width=max(1, size // 32))
        
        # Draw paper
        paper_margin = margin * 3
        paper_color = (255, 255, 255, 255)
        draw.rectangle([
            paper_margin, 
            margin * 4, 
            size - paper_margin, 
            size - paper_margin
        ], fill=paper_color, outline=(0, 0, 0, 255), width=max(1, size // 32))
        
        # Draw text lines (if icon is large enough)
        if size >= 32:
            line_color = (0, 0, 0, 255)
            line_y_start = margin * 5
            line_spacing = max(2, size // 16)
            line_count = min(3, (size - margin * 6) // line_spacing)
            
            for i in range(line_count):
                y = line_y_start + (i * line_spacing)
                draw.line([
                    paper_margin + margin, 
                    y, 
                    size - paper_margin - margin, 
                    y
                ], fill=line_color, width=max(1, size // 64))
        
        images.append(image)
    
    return images


def save_icon():
    """Save icon to resources directory"""
    # Ensure resources directory exists
    resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create icon images
    images = create_icon()
    
    # Save as .ico file
    icon_path = os.path.join(resources_dir, 'icon.ico')
    images[0].save(
        icon_path, 
        format='ICO', 
        sizes=[(img.width, img.height) for img in images]
    )
    
    print(f"Icon saved to: {icon_path}")
    return icon_path


if __name__ == "__main__":
    save_icon()
