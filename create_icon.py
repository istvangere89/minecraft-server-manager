"""
Helper script to create a simple Minecraft-themed icon.
This creates a basic .ico file for the application.
Run this once before building the executable.
"""

try:
    from PIL import Image, ImageDraw
    import os
    
    # Create a simple Minecraft-like icon (16x16 green block)
    size = 256
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw a green square (Minecraft grass block)
    margin = 20
    draw.rectangle(
        [(margin, margin), (size - margin, size - margin)],
        fill=(52, 168, 83, 255),
        outline=(34, 110, 54, 255),
        width=3
    )
    
    # Draw a pattern to represent dirt
    block_size = (size - 2 * margin) // 3
    for i in range(3):
        for j in range(3):
            x1 = margin + i * block_size
            y1 = margin + j * block_size
            x2 = x1 + block_size
            y2 = y1 + block_size
            if (i + j) % 2 == 0:
                draw.rectangle([(x1, y1), (x2, y2)], outline=(34, 110, 54, 255))
    
    # Create assets directory if it doesn't exist
    os.makedirs('assets', exist_ok=True)
    
    # Save as .ico
    icon.save('assets/app_icon.ico')
    print("✓ Icon created successfully at: assets/app_icon.ico")
    
except ImportError:
    print("PIL (Pillow) not installed.")
    print("To create a custom icon, install Pillow:")
    print("  pip install Pillow")
    print("\nOr download a free Minecraft icon from:")
    print("  - https://www.minecraft.net/")
    print("  - Convert PNG to ICO using an online tool")
    print("  - Save to: assets/app_icon.ico")
except Exception as e:
    print(f"Error creating icon: {e}")
