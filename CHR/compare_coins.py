#!/usr/bin/env python3
"""
Extract coin pop animation sprites - trying different sources for frame 1.
"""

from PIL import Image
import os

def get_tile_pixels(img, tile_index):
    col = tile_index % 16
    row = tile_index // 16
    x0 = col * 8
    y0 = row * 8
    pixels = []
    for y in range(8):
        row_pixels = []
        for x in range(8):
            idx = img.getpixel((x0 + x, y0 + y))
            row_pixels.append(idx)
        pixels.append(row_pixels)
    return pixels

def get_8x16_sprite(img, top_tile_index):
    top = get_tile_pixels(img, top_tile_index)
    bottom = get_tile_pixels(img, top_tile_index + 1)
    return top + bottom

def print_sprite_ascii(pixels, name=""):
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    if name:
        print(f"\n{name}:")
    for row in pixels:
        print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'
chr078 = Image.open(os.path.join(chr_dir, 'chr078.pcx'))
chr079 = Image.open(os.path.join(chr_dir, 'chr079.pcx'))

# Compare options for frame 1 (pattern $4F, tiles 14-15)
print("Options for Frame 1 (angled coin):")
print_sprite_ascii(get_8x16_sprite(chr078, 14), "chr078 tiles 14-15")
print_sprite_ascii(get_8x16_sprite(chr079, 14), "chr079 tiles 14-15")

# Let's also see the full coin in chr079
print_sprite_ascii(get_8x16_sprite(chr079, 12), "chr079 tiles 12-13 (full front)")
