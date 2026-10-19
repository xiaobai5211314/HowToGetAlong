#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《人情世故指南》专属高清图标资产"""

from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def create_brand_icon(size=180, radius=42):
    # 创建超采样画布
    scale = 4
    s = size * scale
    r = radius * scale
    
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制 Claude 标志性陶土红背景圆角矩形
    brand_color = (201, 100, 66, 255) # #c96442
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=brand_color)
    
    # 绘制对话/相处微标（双人沟通气泡符号）
    # 大气泡
    bw = int(s * 0.54)
    bh = int(s * 0.38)
    bx = int((s - bw) / 2)
    by = int(s * 0.28)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(r * 0.45), fill=(255, 255, 255, 255))
    
    # 气泡小尾巴
    tail_pts = [
        (bx + int(bw * 0.3), by + bh - 2),
        (bx + int(bw * 0.15), by + bh + int(s * 0.12)),
        (bx + int(bw * 0.45), by + bh - 2)
    ]
    draw.polygon(tail_pts, fill=(255, 255, 255, 255))
    
    # 内部 3 个小圆点
    dot_r = int(s * 0.032)
    dot_y = by + int(bh / 2)
    cx = bx + int(bw / 2)
    dx = int(bw * 0.22)
    draw.ellipse([cx - dx - dot_r, dot_y - dot_r, cx - dx + dot_r, dot_y + dot_r], fill=brand_color)
    draw.ellipse([cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r], fill=brand_color)
    draw.ellipse([cx + dx - dot_r, dot_y - dot_r, cx + dx + dot_r, dot_y + dot_r], fill=brand_color)
    
    # 下采样回目标尺寸（抗锯齿）
    img_out = img.resize((size, size), Image.Resampling.LANCZOS)
    return img_out

def main():
    # 1. apple-touch-icon.png (180x180)
    icon_180 = create_brand_icon(180, 42)
    icon_180.save(ROOT / 'apple-touch-icon.png', 'PNG')
    print("Saved apple-touch-icon.png")
    
    # 2. logo.png (128x128)
    logo_128 = create_brand_icon(128, 30)
    logo_128.save(ROOT / 'logo.png', 'PNG')
    print("Saved logo.png")
    
    # 3. favicon.ico (包含多种尺寸)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    ico_imgs = [create_brand_icon(sz[0], int(sz[0] * 0.24)) for sz in sizes]
    ico_imgs[0].save(
        ROOT / 'favicon.ico',
        format='ICO',
        sizes=sizes,
        append_images=ico_imgs[1:]
    )
    print("Saved favicon.ico")

if __name__ == '__main__':
    main()
