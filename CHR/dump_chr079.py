#!/usr/bin/env python3
"""
Detailed scan of chr079 ($4F) - the common gameplay sprite bank.
Show ALL 64 tiles to find coin and score sprites.
"""

from PIL import Image
import os

TILE_SIZE = 8
TILES_PER_ROW = 16

def get_tile_pixels(img, tile_index):
    """Extract 8x8 pixel data for a tile given its index in the PCX."""
    col = tile_index % TILES_PER_ROW
    row = tile_index // TILES_PER_ROW
    x0 = col * TILE_SIZE
    y0 = row * TILE_SIZE
    
    pixels = []
    for y in range(TILE_SIZE):
        row_pixels = []
        for x in range(TILE_SIZE):
            row_pixels.append(img.getpixel((x0 + x, y0 + y)))
        pixels.append(row_pixels)
    return pixels

def print_tile_ascii(pixels, indent=""):
    """Print ASCII representation of a tile."""
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    for row in pixels:
        print(indent + ''.join(ASCII_MAP.get(p, '?') for p in row))

def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check chr079 - the main gameplay sprite bank
    chr_path = os.path.join(chr_dir, 'chr079.pcx')
    
    print("="*60)
    print("CHR079 ($4F) - FULL TILE DUMP")
    print("="*60)
    print("""
Looking for:
- Coin sprites (spinning animation, 8x8 each frame)
- Score "100" sprites: "1" and "00" digits
""")
    
    img = Image.open(chr_path)
    print(f"Image: {img.size}, mode: {img.mode}")
    print(f"Total tiles: 64 (4 rows x 16 columns)\n")
    
    # Print all 64 tiles
    for tile_idx in range(64):
        row = tile_idx // 16
        col = tile_idx % 16
        print(f"Tile {tile_idx:2d} (${tile_idx:02X}) [row {row}, col {col}]:")
        pixels = get_tile_pixels(img, tile_idx)
        print_tile_ascii(pixels, "  ")
        print()

if __name__ == '__main__':
    main()
