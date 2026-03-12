"""
Generate a modern app icon for ChatBot.
Creates both .icns (macOS) and .ico (Windows) formats.
"""

from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 512


def create_icon():
    """Create a modern gradient icon with a lightning bolt symbol."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background with gradient effect
    # Base: dark navy
    for i in range(SIZE):
        ratio = i / SIZE
        r = int(26 + (61 - 26) * ratio)
        g = int(27 + (89 - 27) * ratio)
        b = int(38 + (161 - 38) * ratio)
        draw.line([(0, i), (SIZE, i)], fill=(r, g, b, 255))

    # Apply rounded corners by masking
    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = SIZE // 5
    mask_draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=radius, fill=255)
    img.putalpha(mask)

    # Draw lightning bolt
    cx, cy = SIZE // 2, SIZE // 2
    bolt_points = [
        (cx + 10, cy - 180),   # top
        (cx - 60, cy + 10),    # mid-left
        (cx + 10, cy + 10),    # mid-center
        (cx - 10, cy + 180),   # bottom
        (cx + 60, cy - 10),    # mid-right
        (cx - 10, cy - 10),    # mid-center-upper
    ]

    # Glow effect
    for offset in range(12, 0, -2):
        glow_alpha = int(30 * (1 - offset / 12))
        glow_color = (122, 162, 247, glow_alpha)
        shifted = [(x, y) for x, y in bolt_points]
        draw.polygon(shifted, fill=glow_color)

    # Main bolt - bright accent blue
    draw.polygon(bolt_points, fill=(122, 162, 247, 255))

    # Inner highlight
    inner_points = [
        (cx + 10, cy - 150),
        (cx - 40, cy + 5),
        (cx + 10, cy + 5),
        (cx - 5, cy + 150),
        (cx + 40, cy - 5),
        (cx - 5, cy - 5),
    ]
    draw.polygon(inner_points, fill=(192, 202, 245, 180))

    return img


def save_icons(img):
    """Save the icon in multiple formats."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Save PNG
    png_path = os.path.join(assets_dir, "icon.png")
    img.save(png_path, "PNG")
    print(f"Saved {png_path}")

    # Save ICO (Windows) - multiple sizes
    ico_path = os.path.join(assets_dir, "icon.ico")
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [img.resize(s, Image.LANCZOS) for s in ico_sizes]
    ico_images[0].save(ico_path, format="ICO", sizes=ico_sizes, append_images=ico_images[1:])
    print(f"Saved {ico_path}")

    # Save ICNS (macOS) - via iconutil requires specific sizes
    # We'll create individual PNGs for iconutil
    iconset_dir = os.path.join(assets_dir, "ChatBot.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    icns_sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
    }

    for name, size in icns_sizes.items():
        resized = img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(iconset_dir, name), "PNG")

    print(f"Saved iconset to {iconset_dir}")
    return assets_dir, iconset_dir


if __name__ == "__main__":
    icon = create_icon()
    assets_dir, iconset_dir = save_icons(icon)
    print(f"\nAssets saved to: {assets_dir}")
    print("   Run `iconutil -c icns assets/ChatBot.iconset` to create .icns on macOS")
