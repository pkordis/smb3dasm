#!/usr/bin/env python3
"""
Look at chr023 around tiles 26-27 and 8-9 for score popup.
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

def print_tile_ascii(pixels, name=""):
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    if name:
        print(f"{name}")
    for row in pixels:
        print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'

# Check chr023 since that has the HUD digits
chr023 = Image.open(os.path.join(chr_dir, 'chr023.pcx'))

print("CHR023 - possible score popup locations:")
print("\nTiles 26+27 (for pattern $5B):")
print_tile_ascii(get_8x16_sprite(chr023, 26))

print("\nTiles 8+9 (for pattern $69):")
print_tile_ascii(get_8x16_sprite(chr023, 8))

# Actually, let me look at what 8x8 tiles might be combined
# The 8x8 digits are at tiles $30-$39 (48-57)
print("\n\nIndividual HUD digits (8x8):")
for i, digit in enumerate(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
    print(f"\nDigit '{digit}' - tile {48+i} (${48+i:02X}):")
    print_tile_ascii(get_tile_pixels(chr023, 48+i))
