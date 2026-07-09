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


def render_minimal(size, game_name):
    """Render a clean, flat, minimal style asset for the given size."""
    w, h = size

    # Flat background color
    bg_color = (24, 26, 32)
    accent_color = (90, 200, 250)
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Thin accent line near the bottom
    line_y = int(h * 0.82)
    draw.rectangle([(0, line_y), (w, line_y + max(2, h // 200))], fill=accent_color)

    # Centered title text
    font_size = max(24, w // 13)
    font = get_font(font_size)
    text = game_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) / 2, (h - th) / 2 - h * 0.03

    draw.text((tx, ty), text, font=font, fill=(245, 245, 245))

    return img


def render_neon(size, game_name):
    """Render a vibrant, neon cyberpunk style asset for the given size."""
    w, h = size

    # Dark blue-black background
    img = Image.new("RGB", (w, h), (5, 5, 15))
    draw = ImageDraw.Draw(img)

    # Diagonal-ish gradient using horizontal bands for a synthwave feel
    for y in range(h):
        t = y / h
        r = int(5 + t * 25)
        g = int(5 + t * 5)
        b = int(30 + t * 60)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Horizon glow lines (like a synthwave grid horizon)
    horizon_y = int(h * 0.65)
    grid_color = (255, 0, 180)
    for i in range(6):
        y = horizon_y + i * max(6, h // 60)
        alpha_line_color = tuple(min(255, c + i * 5) for c in grid_color)
        draw.line([(0, y), (w, y)], fill=alpha_line_color, width=1)

    # Neon title text with cyan + magenta glow
    font_size = max(24, w // 11)
    font = get_font(font_size)
    text = game_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) / 2, (h - th) / 2 - h * 0.08

    for glow_color, offset in [((0, 255, 255), 10), ((255, 0, 200), 6)]:
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.text((tx, ty), text, font=font, fill=(*glow_color, 60))
        glow = glow.filter(ImageFilter.GaussianBlur(offset))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255))

    return img


def render_vaporwave(size, game_name):
    """Render a pastel pink/purple vaporwave/synthwave sunset style asset."""
    w, h = size

    img = Image.new("RGB", (w, h), (20, 10, 40))
    draw = ImageDraw.Draw(img)

    # Sunset gradient: purple top -> pink -> orange near horizon
    top_color = (40, 20, 80)
    mid_color = (220, 60, 140)
    bottom_color = (255, 170, 90)
    horizon_y = int(h * 0.6)

    for y in range(horizon_y):
        t = y / horizon_y
        r = int(top_color[0] + (mid_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (mid_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (mid_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    for y in range(horizon_y, h):
        t = (y - horizon_y) / max(1, (h - horizon_y))
        r = int(mid_color[0] + (bottom_color[0] - mid_color[0]) * t)
        g = int(mid_color[1] + (bottom_color[1] - mid_color[1]) * t)
        b = int(mid_color[2] + (bottom_color[2] - mid_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Sun circle sitting on the horizon
    sun_radius = int(w * 0.14)
    sun_center = (w // 2, horizon_y)
    draw.ellipse(
        [
            (sun_center[0] - sun_radius, sun_center[1] - sun_radius),
            (sun_center[0] + sun_radius, sun_center[1] + sun_radius),
        ],
        fill=(255, 210, 120),
    )
    # A few horizontal "stripes" cut into the sun for retro sun effect
    for i in range(4):
        stripe_y = sun_center[1] - sun_radius + int(sun_radius * 0.5) + i * max(4, sun_radius // 5)
        draw.rectangle([(sun_center[0] - sun_radius, stripe_y), (sun_center[0] + sun_radius, stripe_y + max(2, sun_radius // 12))], fill=mid_color)

    # Perspective grid below the horizon
    grid_color = (255, 255, 255)
    vanishing_x = w // 2
    for i in range(-6, 7):
        x_bottom = vanishing_x + i * (w // 8)
        draw.line([(vanishing_x, horizon_y), (x_bottom, h)], fill=(*grid_color, 255) if False else grid_color, width=1)
    for j in range(1, 6):
        y = horizon_y + int((h - horizon_y) * (j / 6) ** 1.5)
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

    # Title text, centered above horizon
    font_size = max(24, w // 11)
    font = get_font(font_size)
    text = game_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) / 2, horizon_y * 0.35 - th / 2

    for glow_color, offset in [((0, 230, 255), 8)]:
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.text((tx, ty), text, font=font, fill=(*glow_color, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(offset))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    draw = ImageDraw.Draw(img)
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255))

    return img


def render_pixel(size, game_name):
    """Render a chunky pixel-art style asset by drawing at low-res and upscaling."""
    w, h = size
    scale = max(4, w // 100)
    small_w, small_h = max(1, w // scale), max(1, h // scale)

    small = Image.new("RGB", (small_w, small_h), (18, 18, 28))
    draw = ImageDraw.Draw(small)

    # Simple checkerboard-ish pixel background pattern
    block = max(2, small_w // 20)
    palette = [(18, 18, 28), (28, 28, 46), (40, 40, 64)]
    for by in range(0, small_h, block):
        for bx in range(0, small_w, block):
            color = palette[(bx // block + by // block) % len(palette)]
            draw.rectangle([bx, by, bx + block, by + block], fill=color)

    small = small.resize((w, h), Image.NEAREST)

    draw = ImageDraw.Draw(small)
    font_size = max(20, w // 14)
    font = get_font(font_size)
    text = game_name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx, ty = (w - tw) / 2, (h - th) / 2

    # Hard drop shadow for a pixel/8-bit look (no blur)
    shadow_offset = max(2, w // 250)
    draw.text((tx + shadow_offset, ty + shadow_offset), text, font=font, fill=(0, 0, 0))
    draw.text((tx, ty), text, font=font, fill=(120, 255, 120))

    return small


STYLES = {
    "retro": render_retro,
    "minimal": render_minimal,
    "neon": render_neon,
    "vaporwave": render_vaporwave,
    "pixel": render_pixel,
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
