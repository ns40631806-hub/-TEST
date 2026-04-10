#!/usr/bin/env python3
"""
Card News Generator
Creates beautiful social media card images with Korean text support
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import sys


def resize_and_crop(img, target_width, target_height):
    """
    Resize and crop image to fit target dimensions while maintaining aspect ratio
    Centers the crop
    """
    width, height = img.size

    target_ratio = target_width / target_height
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * current_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        left = (new_width - target_width) // 2
        img = img.crop((left, 0, left + target_width, target_height))
    else:
        new_width = target_width
        new_height = int(new_width / current_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        top = (new_height - target_height) // 2
        img = img.crop((0, top, target_width, top + target_height))

    return img


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def create_card_news(
    title,
    content,
    output_path,
    bg_color="#F5F3EE",
    text_color="#1A1A1A",
    width=600,
    height=600,
    title_size=48,
    content_size=28,
    number=None,
    bg_image_path=None,
    overlay_opacity=0.5
):
    """
    Generate a card news image with vertically centered content
    """

    if bg_image_path and os.path.exists(bg_image_path):
        try:
            bg_img = Image.open(bg_image_path)
            if bg_img.mode != 'RGB':
                bg_img = bg_img.convert('RGB')
            bg_img = resize_and_crop(bg_img, width, height)
            img = bg_img

            overlay = Image.new('RGB', (width, height), (0, 0, 0))
            img = Image.blend(img, overlay, overlay_opacity)

            if text_color == "#1A1A1A":
                text_color = "#FFFFFF"

        except Exception as e:
            print(f"Warning: Could not load background image {bg_image_path}: {e}", file=sys.stderr)
            print("Falling back to solid color background", file=sys.stderr)
            img = Image.new('RGB', (width, height), bg_color)
    else:
        img = Image.new('RGB', (width, height), bg_color)

    draw = ImageDraw.Draw(img)

    padding = 40
    max_text_width = width - (padding * 2)

    # Font loading - try multiple paths
    font_paths_bold = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    ]
    font_paths_regular = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]

    def load_font(paths, size):
        for path in paths:
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
        print("Warning: Korean font not found, using default font", file=sys.stderr)
        return ImageFont.load_default()

    title_font = load_font(font_paths_bold, title_size)
    content_font = load_font(font_paths_regular, content_size)
    number_font = load_font(font_paths_bold, 60)

    # Calculate total content height
    number_height = 0
    if number is not None:
        number_text = str(number)
        bbox = draw.textbbox((0, 0), number_text, font=number_font)
        number_height = bbox[3] - bbox[1] + 40

    title_lines = []
    for line in title.split('\n'):
        wrapped = wrap_text(line, title_font, max_text_width, draw)
        title_lines.extend(wrapped)

    title_height = 0
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        title_height += bbox[3] - bbox[1] + 10

    content_lines = []
    for line in content.split('\n'):
        wrapped = wrap_text(line, content_font, max_text_width, draw)
        content_lines.extend(wrapped)

    content_height = 0
    for line in content_lines:
        bbox = draw.textbbox((0, 0), line, font=content_font)
        content_height += bbox[3] - bbox[1] + 8

    spacing_between = 30
    total_content_height = number_height + title_height + spacing_between + content_height
    start_y = (height - total_content_height) // 2

    current_y = start_y

    if number is not None:
        number_text = str(number)
        bbox = draw.textbbox((0, 0), number_text, font=number_font)
        number_width = bbox[2] - bbox[0]
        number_x = (width - number_width) // 2
        draw.text((number_x, current_y), number_text, fill=text_color, font=number_font)
        current_y += bbox[3] - bbox[1] + 40

    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        x = (width - line_width) // 2
        draw.text((x, current_y), line, fill=text_color, font=title_font)
        current_y += line_height + 10

    current_y += spacing_between

    for line in content_lines:
        bbox = draw.textbbox((0, 0), line, font=content_font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        x = (width - line_width) // 2
        draw.text((x, current_y), line, fill=text_color, font=content_font)
        current_y += line_height + 8

    img.save(output_path, 'PNG', quality=95)
    print(f"Card generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate card news images with Korean text support'
    )

    parser.add_argument('--title', required=True, help='Main title text')
    parser.add_argument('--content', required=True, help='Body content text')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--bg-color', default='#F5F3EE', help='Background color (hex)')
    parser.add_argument('--text-color', default='#1A1A1A', help='Text color (hex)')
    parser.add_argument('--width', type=int, default=600, help='Image width (default: 600)')
    parser.add_argument('--height', type=int, default=600, help='Image height (default: 600)')
    parser.add_argument('--title-size', type=int, default=48, help='Title font size (default: 48)')
    parser.add_argument('--content-size', type=int, default=28, help='Content font size (default: 28)')
    parser.add_argument('--number', type=int, help='Optional number badge')
    parser.add_argument('--bg-image', help='Path to background image')
    parser.add_argument('--overlay-opacity', type=float, default=0.5, help='Opacity of dark overlay (0.0-1.0)')

    args = parser.parse_args()

    create_card_news(
        title=args.title,
        content=args.content,
        output_path=args.output,
        bg_color=args.bg_color,
        text_color=args.text_color,
        width=args.width,
        height=args.height,
        title_size=args.title_size,
        content_size=args.content_size,
        number=args.number,
        bg_image_path=args.bg_image,
        overlay_opacity=args.overlay_opacity
    )


if __name__ == '__main__':
    main()
