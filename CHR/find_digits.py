#!/usr/bin/env python3
"""
Look for score popup digits more carefully.

The score popup in SMB3 uses 8x16 sprites arranged side by side.
Score_PatternLeft and Score_PatternRight give 8x16 patterns for each half.

100 pts: Left=$5B, Right=$69

Pattern $5B: tiles $5A, $5B (bank-relative 26,27 if bank $4E/chr078)
Pattern $69: tiles $68, $69 (bank-relative 8,9 if bank $4F/chr079)

But these might use different banks during gameplay. Let's search
for digit-shaped patterns in 8x16 format across all banks.
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

# The score popup might use different banks. Let's check chr020-023
# which are used in the world map

banks = {}
for num in list(range(20, 36)) + [78, 79]:
    path = os.path.join(chr_dir, f'chr{num:03d}.pcx')
    if os.path.exists(path):
        banks[num] = Image.open(path)

print(f"Loaded {len(banks)} banks: {sorted(banks.keys())}")

print("\n" + "="*60)
print("LOOKING FOR DIGIT '1' PATTERNS")
print("A '1' should be a vertical line, narrow")
print("="*60)

# Looking for tiles with mostly vertical content
for bank_num, img in sorted(banks.items()):
    for tile_idx in range(64):  # Scan all tiles
        pix = get_tile_pixels(img, tile_idx)
        # Check if this looks like a '1' - mostly central vertical
        filled_cols = [sum(1 for row in pix if row[x] > 0) for x in range(8)]
        # '1' typically has most pixels in center columns
        if sum(filled_cols) >= 16 and max(filled_cols) >= 6:
            # Check if narrow (only 2-3 columns have significant content)
            active_cols = sum(1 for c in filled_cols if c >= 4)
            if active_cols <= 4 and active_cols >= 1:
                print(f"\nchr{bank_num:03d} tile {tile_idx} looks like '1':")
                ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
                for row in pix:
                    print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

print("\n" + "="*60)
print("LOOKING FOR DIGIT '0' PATTERNS (oval/ring)")
print("="*60)

for bank_num, img in sorted(banks.items()):
    for tile_idx in range(64):
        pix = get_tile_pixels(img, tile_idx)
        # Check for oval/ring shape - edges have content, center is empty
        total = sum(1 for row in pix for p in row if p > 0)
        # Check center emptiness (cols 3-4, rows 2-5)
        center_empty = sum(1 for y in range(2, 6) for x in range(3, 5) if pix[y][x] == 0)
        # Edge filled
        edge_filled = sum(1 for y in range(8) for x in [0, 7] if pix[y][x] > 0)
        
        if total >= 24 and center_empty >= 6 and edge_filled >= 6:
            print(f"\nchr{bank_num:03d} tile {tile_idx} looks like '0':")
            ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
            for row in pix:
                print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))
