#!/usr/bin/env python3
"""
Find the "100" score popup sprites.

Score patterns from dasm:
- 100 pts: Left=$5B, Right=$69

In 8x16 sprite mode:
- Pattern $5B uses tiles $5A+$5B -> bank-relative 26+27 (if bank $4E/chr078)
- Pattern $69 uses tiles $68+$69 -> bank-relative 8+9 (if bank $4F/chr079)

Let's scan multiple banks to find where the score digits actually are.
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
        print(f"{name}:")
    for row in pixels:
        print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'

# Load several banks
banks = {}
for num in [32, 33, 34, 35, 78, 79]:
    path = os.path.join(chr_dir, f'chr{num:03d}.pcx')
    if os.path.exists(path):
        banks[num] = Image.open(path)
        print(f"Loaded chr{num:03d}")

print("\n" + "="*60)
print("SEARCHING FOR SCORE SPRITES (digits 1, 0, 0)")
print("="*60)

# Score sprites are typically 8x8 each, not 8x16
# Let's look for digit-shaped tiles

# For pattern $5B (left half of "100"):
# In various banks, tile 26+27 would be:
for bank_num, img in banks.items():
    print(f"\nchr{bank_num:03d} - tiles 26-27 (pattern $5B area):")
    print_sprite_ascii(get_8x16_sprite(img, 26))

print("\n" + "="*60)

# For pattern $69 (right half, the "00"):
# Tile 8+9 in various banks
for bank_num, img in banks.items():
    print(f"\nchr{bank_num:03d} - tiles 8-9 (pattern $69 area):")
    print_sprite_ascii(get_8x16_sprite(img, 8))

print("\n" + "="*60)
print("SCANNING FOR NUMBER-LIKE TILES")
print("="*60)

# Let's look for tiles that might be digits (0 and 1)
# Tiles with circular patterns (for 0) or vertical lines (for 1)
for bank_num, img in banks.items():
    print(f"\n--- chr{bank_num:03d} tiles 24-31 ---")
    for tile_idx in range(24, 32):
        pixels = get_tile_pixels(img, tile_idx)
        filled = sum(1 for row in pixels for p in row if p > 0)
        if filled > 8:  # Has some content
            print(f"\nTile {tile_idx} (${tile_idx:02X}):")
            ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
            for row in pixels:
                print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))
