#!/usr/bin/env python3
"""
Dump chr020-023 tiles to find score digits.
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

def print_tile_ascii(pixels, name=""):
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    if name:
        print(f"{name}")
    for row in pixels:
        print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'

for num in range(20, 24):
    path = os.path.join(chr_dir, f'chr{num:03d}.pcx')
    if os.path.exists(path):
        img = Image.open(path)
        print(f"\n{'='*60}")
        print(f"CHR{num:03d}")
        print(f"{'='*60}")
        for tile_idx in range(64):  # All tiles
            pix = get_tile_pixels(img, tile_idx)
            # Only show non-empty tiles
            filled = sum(1 for row in pix for p in row if p > 0)
            if filled > 5:
                print(f"\nTile {tile_idx} (${tile_idx:02X}):")
                print_tile_ascii(pix)
