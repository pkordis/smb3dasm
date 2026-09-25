#!/usr/bin/env python3
"""
Detailed scan of chr078 ($4E) - patterns $40-$5F bank.
This is where coin patterns $49, $4D would actually be.
"""

from PIL import Image
import os

TILE_SIZE = 8
TILES_PER_ROW = 16

def get_tile_pixels(img, tile_index):
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
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    for row in pixels:
        print(indent + ''.join(ASCII_MAP.get(p, '?') for p in row))

def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("="*60)
    print("CHR078 ($4E) - PATTERNS $40-$5F BANK")
    print("="*60)
    print("""
Coin patterns from dasm: $49, $4F, $4D, $4F
- $49 is in range $40-$5F, uses BankSel+4 = $4E (chr078)
- Local index = $49 - $40 = $09

For 8x16 sprites, pattern $49 uses:
- Top tile: $48 (local index 8)
- Bottom tile: $49 (local index 9)

Looking for coin frames at local indices:
- $48/$49 (8/9) - pattern $49
- $4C/$4D (12/13) - pattern $4D
- $4E/$4F (14/15) - pattern $4F
""")
    
    chr_path = os.path.join(chr_dir, 'chr078.pcx')
    img = Image.open(chr_path)
    print(f"Image: {img.size}, mode: {img.mode}\n")
    
    # Show the relevant coin tiles
    coin_indices = [
        (8, 9, "Pattern $49 (first coin frame)"),
        (12, 13, "Pattern $4D (second coin frame)"),
        (14, 15, "Pattern $4F (third coin frame)"),
    ]
    
    for top, bottom, desc in coin_indices:
        print(f"\n{desc}:")
        print(f"  Top tile (local ${top:02X}, global ${top+0x40:02X}):")
        pixels = get_tile_pixels(img, top)
        print_tile_ascii(pixels, "    ")
        print(f"  Bottom tile (local ${bottom:02X}, global ${bottom+0x40:02X}):")
        pixels = get_tile_pixels(img, bottom)
        print_tile_ascii(pixels, "    ")
    
    print("\n" + "="*60)
    print("ALL TILES IN CHR078:")
    print("="*60 + "\n")
    
    for tile_idx in range(64):
        print(f"Tile {tile_idx:2d} (local ${tile_idx:02X}, global ${tile_idx+0x40:02X}):")
        pixels = get_tile_pixels(img, tile_idx)
        print_tile_ascii(pixels, "  ")
        print()

if __name__ == '__main__':
    main()
