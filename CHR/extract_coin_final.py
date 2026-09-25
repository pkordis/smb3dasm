#!/usr/bin/env python3
"""
Extract coin pop animation sprites from SMB3 CHR data.

For a spinning coin animation:
- Frame 0: Full front view
- Frame 1: Partial/angled (rotating away)
- Frame 2: Thin edge (side view)
- Frame 3: Partial/angled (rotating back) - reuse frame 1 with H-flip

Best sources based on visual inspection:
- Full coin: chr079 tiles 12-13 OR chr078 tiles 8-9
- Thin edge: chr078 tiles 12-13
- Partial/angled: chr079 tiles 14-15
"""

from PIL import Image
import os

TILE_SIZE = 8
TILES_PER_ROW = 16

# Coin palette - gold/orange with white highlight
COIN_PALETTE = {
    0: (0, 0, 0, 0),           # Transparent
    1: (0x00, 0x00, 0x00, 255), # Black outline  
    2: (0xFC, 0xA0, 0x44, 255), # Orange/gold
    3: (0xFC, 0xFC, 0xFC, 255), # White highlight
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
            idx = img.getpixel((x0 + x, y0 + y))
            row_pixels.append(idx)
        pixels.append(row_pixels)
    return pixels


def get_8x16_sprite(img, top_tile_index):
    top = get_tile_pixels(img, top_tile_index)
    bottom = get_tile_pixels(img, top_tile_index + 1)
    return top + bottom


def save_sprite(pixels, filename, palette, width=8, height=16):
    out = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            idx = pixels[y][x]
            color = palette.get(idx, (255, 0, 255, 255))
            out.putpixel((x, y), color)
    out.save(filename)
    print(f"Saved: {filename}")


def print_sprite_ascii(pixels, name=""):
    ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
    if name:
        print(f"{name}:")
    for row in pixels:
        print('  ' + ''.join(ASCII_MAP.get(p, '?') for p in row))


def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    
    project_coin_dir = os.path.join(
        chr_dir, '..', 'super-mario-bros-3',
        'src', 'main', 'resources', 'sprites', 'object', 'coin'
    )
    
    os.makedirs(project_coin_dir, exist_ok=True)
    
    chr078 = Image.open(os.path.join(chr_dir, 'chr078.pcx'))
    chr079 = Image.open(os.path.join(chr_dir, 'chr079.pcx'))
    
    print("="*60)
    print("EXTRACTING COIN ANIMATION FRAMES")
    print("="*60)
    
    # Frame 0: Full front view - chr079 tiles 12-13 (cleaner circular shape)
    print("\nFrame 0 (full front) - chr079 tiles 12-13:")
    pixels = get_8x16_sprite(chr079, 12)
    print_sprite_ascii(pixels)
    save_sprite(pixels, os.path.join(project_coin_dir, 'frame_0.png'), COIN_PALETTE)
    
    # Frame 1: Angled view - chr079 tiles 14-15
    print("\nFrame 1 (angled) - chr079 tiles 14-15:")
    pixels = get_8x16_sprite(chr079, 14)
    print_sprite_ascii(pixels)
    save_sprite(pixels, os.path.join(project_coin_dir, 'frame_1.png'), COIN_PALETTE)
    
    # Frame 2: Thin edge - chr078 tiles 12-13
    print("\nFrame 2 (thin edge) - chr078 tiles 12-13:")
    pixels = get_8x16_sprite(chr078, 12)
    print_sprite_ascii(pixels)
    save_sprite(pixels, os.path.join(project_coin_dir, 'frame_2.png'), COIN_PALETTE)
    
    # Frame 3 reuses Frame 1 with H-flip (handled in Java code)
    
    print("\n" + "="*60)
    print("DONE! 3 unique frames extracted.")
    print("="*60)
    print("""
Animation sequence:
  Frame 0: Full front coin
  Frame 1: Angled coin (rotating)
  Frame 2: Thin edge (side view)
  Frame 3: Reuse Frame 1 with H-flip

Java animation cycle: 0 -> 1 -> 2 -> 1(flip) -> repeat
""")


if __name__ == '__main__':
    main()
