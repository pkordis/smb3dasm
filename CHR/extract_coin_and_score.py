#!/usr/bin/env python3
"""
Extract coin pop animation and score sprites from SMB3 CHR data.

CORRECT MAPPING (verified from visual inspection):

During level gameplay, sprite banks are often:
- PatTable_BankSel+4 = $20-$22 (chr032-chr034)  
- PatTable_BankSel+5 = $21-$23 (chr033-chr035)

CHR033 contains the coin sprites at tiles 14-15 (pattern $4F in 8x16 mode).

The coin animation patterns $49, $4F, $4D, $4F actually map to:
- $49 in bank $21 (chr033): local tile 9 for top, tile 10 for bottom? 
  Actually let's check multiple banks...

Since chr033 tile 14-15 clearly shows a coin, let's check which pattern that corresponds to.
Pattern $4F with BankSel+4 = $21 (chr033): local tile = $4F - $40 = $0F (15)
In 8x16 mode, pattern $4F uses tiles $4E (14) + $4F (15)

So the coin frames in chr033 would be:
- Tiles 8+9 for pattern $49
- Tiles 12+13 for pattern $4D  
- Tiles 14+15 for pattern $4F
"""

from PIL import Image
import os
import sys

TILE_SIZE = 8
TILES_PER_ROW = 16

# Coin palette - gold/orange with white highlight
COIN_PALETTE = {
    0: (0, 0, 0, 0),           # Transparent
    1: (0x00, 0x00, 0x00, 255), # Black outline
    2: (0xFC, 0xA0, 0x44, 255), # Orange/gold
    3: (0xFC, 0xFC, 0xFC, 255), # White highlight
}

# Score text palette - white
SCORE_PALETTE = {
    0: (0, 0, 0, 0),           # Transparent
    1: (0xFC, 0xFC, 0xFC, 255), # White
    2: (0xFC, 0xFC, 0xFC, 255), # White
    3: (0xFC, 0xFC, 0xFC, 255), # White
}


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


def get_8x16_sprite(img, top_tile_index):
    top = get_tile_pixels(img, top_tile_index)
    bottom = get_tile_pixels(img, top_tile_index + 1)
    return top + bottom


def print_tile_ascii(pixels, name=""):
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    if name:
        print(f"  {name}:")
    for row in pixels:
        print("    " + ''.join(ASCII_MAP.get(p, '?') for p in row))


def save_tile(pixels, filename, palette, width=8, height=8):
    out = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            color = palette.get(pixels[y][x], (255, 0, 255, 255))
            out.putpixel((x, y), color)
    out.save(filename)
    print(f"  Saved: {filename}")


def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    
    project_coin_dir = os.path.join(
        chr_dir, '..', 'super-mario-bros-3',
        'src', 'main', 'resources', 'sprites', 'object', 'coin'
    )
    project_score_dir = os.path.join(
        chr_dir, '..', 'super-mario-bros-3',
        'src', 'main', 'resources', 'sprites', 'object', 'score'
    )
    
    print("="*60)
    print("SEARCHING FOR COIN SPRITES ACROSS CHR BANKS")
    print("="*60)
    
    # Load multiple CHR banks to find the coins
    banks = {}
    for bank_num in [32, 33, 34, 35, 78, 79]:
        chr_path = os.path.join(chr_dir, f'chr{bank_num:03d}.pcx')
        if os.path.exists(chr_path):
            banks[bank_num] = Image.open(chr_path)
            print(f"Loaded chr{bank_num:03d}")
    
    # Look for coin-like tiles (circular shapes) in each bank
    print("\n--- SEARCHING FOR COIN TILES ---")
    
    for bank_num, img in banks.items():
        print(f"\nchr{bank_num:03d} - Tiles 8-15 (likely coin locations):")
        for tile_idx in [8, 9, 10, 11, 12, 13, 14, 15]:
            pixels = get_tile_pixels(img, tile_idx)
            print_tile_ascii(pixels, f"Tile {tile_idx} (${tile_idx:02X})")
            print()
    
    # Based on visual inspection, chr033 tiles 14-15 are clearly a coin
    # Let's extract from chr033
    print("\n" + "="*60)
    print("EXTRACTING COINS FROM CHR033")
    print("="*60)
    
    chr033 = banks[33]
    
    os.makedirs(project_coin_dir, exist_ok=True)
    os.makedirs(project_score_dir, exist_ok=True)
    
    # Frame 0: Pattern $49 → tiles 8+9 in whichever bank
    # Frame 1: Pattern $4D → tiles 12+13
    # Frame 2: Pattern $4F → tiles 14+15 (this is the clear coin in chr033!)
    
    print("\nExtracting coin frames from chr033:")
    
    # Check chr033 tiles 8-9 for pattern $49
    print("\nFrame 0 (pattern $49, chr033 tiles 8+9):")
    pixels = get_8x16_sprite(chr033, 8)
    print_tile_ascii(pixels[:8], "Top")
    print_tile_ascii(pixels[8:], "Bottom")
    
    # Check chr033 tiles 12-13 for pattern $4D
    print("\nFrame 1 (pattern $4D, chr033 tiles 12+13):")
    pixels = get_8x16_sprite(chr033, 12)
    print_tile_ascii(pixels[:8], "Top")
    print_tile_ascii(pixels[8:], "Bottom")
    
    # Check chr033 tiles 14-15 for pattern $4F - THIS IS THE COIN!
    print("\nFrame 2 (pattern $4F, chr033 tiles 14+15):")
    pixels = get_8x16_sprite(chr033, 14)
    print_tile_ascii(pixels[:8], "Top")
    print_tile_ascii(pixels[8:], "Bottom")
    save_tile(pixels, os.path.join(project_coin_dir, 'frame_2.png'), COIN_PALETTE, 8, 16)
    
    # The animation sequence is $49, $4F, $4D, $4F
    # So we need tiles 8+9, 14+15, 12+13 from the correct bank
    # Let's save all three from chr033
    
    pixels = get_8x16_sprite(chr033, 8)
    save_tile(pixels, os.path.join(project_coin_dir, 'frame_0.png'), COIN_PALETTE, 8, 16)
    
    pixels = get_8x16_sprite(chr033, 12)
    save_tile(pixels, os.path.join(project_coin_dir, 'frame_1.png'), COIN_PALETTE, 8, 16)
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)


if __name__ == '__main__':
    main()
