#!/usr/bin/env python3
"""
Scan CHR banks to find the coin sprites.

In 8x16 mode:
- Sprites use pattern table 2 (PPU $1000-$1FFF)
- Pattern ID bit 0 is ignored; $49 uses tiles $48+$49
- PatTable_BankSel+2/+3 control $1000-$13FF (patterns $00-$3F)
- PatTable_BankSel+4/+5 control $1400-$1FFF (patterns $40-$7F)

Coin patterns: $49, $4F, $4D → use tiles $48/$49, $4E/$4F, $4C/$4D
These are in the $40-$7F range, so they use BankSel+4/+5.

During gameplay, BankSel+5 is often set to $4F (chr079) for common sprites.
Let's scan chr079 and other likely banks.
"""

from PIL import Image
import os
import sys

TILE_SIZE = 8
TILES_PER_ROW = 16

def get_tile_pixels(img, tile_index):
    """Extract 8x8 pixel data for a tile given its index in the PCX."""
    col = tile_index % TILES_PER_ROW
    row = tile_index // TILES_PER_ROW
    x0 = col * TILE_SIZE
    y0 = row * TILE_SIZE
    
    # Check bounds
    max_tiles = (img.width // TILE_SIZE) * (img.height // TILE_SIZE)
    if tile_index >= max_tiles:
        return None
    
    pixels = []
    for y in range(TILE_SIZE):
        row_pixels = []
        for x in range(TILE_SIZE):
            row_pixels.append(img.getpixel((x0 + x, y0 + y)))
        pixels.append(row_pixels)
    return pixels

def print_tile_ascii(pixels, indent="  "):
    """Print ASCII representation of a tile."""
    if pixels is None:
        print(f"{indent}[out of bounds]")
        return
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    for row in pixels:
        print(indent + ''.join(ASCII_MAP.get(p, '?') for p in row))

def scan_chr_bank(chr_path, bank_name):
    """Scan a CHR bank and show coin-related tiles."""
    if not os.path.exists(chr_path):
        print(f"  {bank_name}: NOT FOUND")
        return
    
    img = Image.open(chr_path)
    max_tiles = (img.width // TILE_SIZE) * (img.height // TILE_SIZE)
    print(f"\n{bank_name}: {img.size}, {max_tiles} tiles")
    
    # In a 1KB CHR bank (64 tiles), pattern $4X maps to tile (X & 0x3F)
    # But the coin uses BankSel+4/+5 which covers patterns $40-$7F
    # Pattern $48 in BankSel+4 → tile 8 (since $48 & 0x3F = 8)
    # But wait - BankSel+4 is for $40-$5F, BankSel+5 is for $60-$7F
    # Actually no - in MMC3:
    # - BankSel+2/+3 are 2KB banks at PPU $1000-$17FF (sprites 0-127)
    # - BankSel+4/+5 are 1KB banks at PPU $1800-$1FFF (sprites 128-191+)
    # 
    # Hmm, let me reconsider. The MMC3 mapper swaps 1KB CHR banks.
    # Each PCX is one 1KB bank = 64 tiles.
    #
    # For 8x16 sprites at pattern $49:
    # - Top tile = $48, Bottom tile = $49
    # - These are at PPU addresses $48*16 and $49*16 = $480 and $490
    # - In the sprite pattern table ($1000 base), that's $1480 and $1490
    # - Which bank covers $1480? Depends on PPU mapping.
    #
    # Let me just show all tiles 0-15 from various banks and we can visually identify the coin.
    
    print("  Tiles 0-15 (possible coin locations):")
    for i in range(min(16, max_tiles)):
        print(f"\n  Tile {i} (${i:02X}):")
        pixels = get_tile_pixels(img, i)
        print_tile_ascii(pixels, "    ")

def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("="*60)
    print("CHR BANK SCAN FOR COIN SPRITES")
    print("="*60)
    print("""
Looking for coin sprites (spinning coin that pops from ? blocks).
The coin should be a circular/oval shape, approximately 8x8 or 8x16.

Coin patterns from dasm: $49, $4F, $4D, $4F
In 8x16 mode, $49 uses tiles $48+$49 (since bit 0 is ignored)

Common sprite CHR banks during gameplay:
- $4E = chr078
- $4F = chr079
- $20-$23 = chr032-chr035 (world map)
""")
    
    # Check several likely CHR banks
    banks_to_check = [
        (78, "chr078 (common sprite bank $4E)"),
        (79, "chr079 (common sprite bank $4F)"),
        (80, "chr080"),
        (81, "chr081"),
        (32, "chr032 (world map sprites)"),
        (33, "chr033 (world map sprites)"),
        (34, "chr034 (world map sprites)"),
        (35, "chr035 (world map sprites)"),
    ]
    
    for bank_num, desc in banks_to_check:
        chr_path = os.path.join(chr_dir, f'chr{bank_num:03d}.pcx')
        scan_chr_bank(chr_path, desc)

if __name__ == '__main__':
    main()
