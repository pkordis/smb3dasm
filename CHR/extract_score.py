#!/usr/bin/env python3
"""
Create score popup sprites matching the original SMB3 format.

The score popup uses two 8x8 sprites side by side:
- Left: "1" digit (8x8)
- Right: "00" (8x8) - but the original uses a single 8x8 glyph

Since we have individual digit tiles, we can create:
- 100_left.png: The "1" digit (8x8)
- 100_right.png: The "00" digits (16x8) OR a compressed "00" (8x8)

Let's create 100_left as 8x8 "1" and 100_right as 8x8 "00" (two zeros squeezed).
Actually, the original game has a dedicated "00" glyph at 8x8. Let's just use
our digit_0 twice side by side for a 16x8 "00", and then scale it in the Java code.

For simplicity, I'll create:
- 100_left.png = 8x8 "1"
- 100_right.png = 8x8 "00" (squeezed together, or just one "0")
"""

from PIL import Image
import os

TILE_SIZE = 8
TILES_PER_ROW = 16

# Score palette - white text  
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
            idx = img.getpixel((x0 + x, y0 + y))
            row_pixels.append(idx)
        pixels.append(row_pixels)
    return pixels


def save_sprite(pixels, filename, palette, width, height):
    out = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            idx = pixels[y][x]
            color = palette.get(idx, (255, 0, 255, 255))
            out.putpixel((x, y), color)
    out.save(filename)
    print(f"Saved: {filename}")


def main():
    chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'
    project_score_dir = r'C:\Users\pkordis\Projects\super-mario-bros-3\src\main\resources\sprites\object\score'
    
    os.makedirs(project_score_dir, exist_ok=True)
    
    chr023 = Image.open(os.path.join(chr_dir, 'chr023.pcx'))
    
    # HUD digits at tiles $30-$39 (48-57): '0'-'9'
    digit_0 = get_tile_pixels(chr023, 48)  # Tile $30 = '0'
    digit_1 = get_tile_pixels(chr023, 49)  # Tile $31 = '1'
    
    # 100_left.png = "1" (8x8)
    save_sprite(digit_1, os.path.join(project_score_dir, '100_left.png'), SCORE_PALETTE, 8, 8)
    
    # 100_right.png = "00" (16x8)
    # This matches the original which has two zeros side by side
    combined_00 = []
    for y in range(8):
        row = digit_0[y] + digit_0[y]
        combined_00.append(row)
    save_sprite(combined_00, os.path.join(project_score_dir, '100_right.png'), SCORE_PALETTE, 16, 8)
    
    # Also save the full "100" for reference
    combined_100 = []
    for y in range(8):
        row = digit_1[y] + digit_0[y] + digit_0[y]
        combined_100.append(row)
    save_sprite(combined_100, os.path.join(project_score_dir, '100.png'), SCORE_PALETTE, 24, 8)


if __name__ == '__main__':
    main()
