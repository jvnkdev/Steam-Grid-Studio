#!/usr/bin/env python3
"""
Steam Grid Studio
Generate custom Steam library artwork (grid capsule, hero banner, logo)
for any game, using style templates.
"""

import argparse
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Steam asset sizes
SIZES = {
    "grid": (600, 900),
    "hero": (1920, 620),
    "logo": (1280, 720),
}


def get_font(size):
    """Try to load a nice font, fall back to default if unavailable."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def apply_scanlines(img, spacing=4, opacity=60):
    """Overlay CRT-style horizontal scanlines."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, img.size[1], spacing):
        draw.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def apply_glitch(img, strength=6):
    """Shift random horizontal slices to create a glitch effect."""
    img = img.copy()
    w, h = img.size
    slice_height = max(4, h // 40)
    for y in range(0, h, slice_height):
        if random.random() < 0.25:
            offset = random.randint(-strength, strength)
            box = (0, y, w, min(y + slice_height, h))
            region = img.crop(box)
            img.paste(region, (offset, y))
    return img


def apply_chromatic_aberration(img, offset=3):
    """Slightly shift the red and blue channels for a CRT color-fringe look."""
    r, g, b, *rest = img.convert("RGBA").split()
    r = Image.new("L", img.size, 0)
    r.paste(img.convert("RGBA").split()[0], (offset, 0))
    b = Image.new("L", img.size, 0)
    b.paste(img.convert("RGBA").split()[2], (-offset, 0))
    merged = Image.merge("RGBA", (r, g, b, img.convert("RGBA").split()[3]))
    return merged


def render_retro(size, game_name):
    """Render a retro CRT/glitch style asset for the given size."""
    w, h = size
    # Dark background with a subtle vertical gradient (deep purple -> black)
    img = Image.new("RGB", (w, h), (10, 8, 20))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(20 + t * 10)
        g = int(8 + t * 4)
        b = int(35 + t * 20)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Neon-ish title text, centered
    font_size = max(24, w // 12)
    font = get_font(font_size)
    text = game_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) / 2, (h - th) / 2

    glow_color = (255, 45, 190)
    for offset in range(6, 0, -2):
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.text((tx, ty), text, font=font, fill=(*glow_color, 40))
        glow = glow.filter(ImageFilter.GaussianBlur(offset))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)
    draw.text((tx, ty), text, font=font, fill=(240, 240, 255))

    # Effects
    img = apply_glitch(img, strength=max(2, w // 200))
    img = apply_chromatic_aberration(img, offset=max(1, w // 400))
    img = apply_scanlines(img.convert("RGBA"), spacing=4, opacity=50)

    return img.convert("RGB")


STYLES = {
    "retro": render_retro,
}


def main():
    parser = argparse.ArgumentParser(description="Generate custom Steam library artwork.")
    parser.add_argument("--game", required=True, help="Name of the game")
    parser.add_argument("--style", default="retro", choices=STYLES.keys(), help="Style template to use")
    parser.add_argument("--output", default="output", help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    render_fn = STYLES[args.style]

    safe_name = "".join(c for c in args.game if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")

    for asset_name, size in SIZES.items():
        img = render_fn(size, args.game)
        out_path = os.path.join(args.output, f"{safe_name}_{asset_name}_{args.style}.png")
        img.save(out_path)
        print(f"Saved {asset_name} ({size[0]}x{size[1]}) -> {out_path}")


if __name__ == "__main__":
    main()
