"""
Extract question block animation tiles from the SMB3 CHR data.

ANALYSIS:
The question block shimmer animation works identically to the brick block.
PatTable_BankSel+1 cycles through banks $60, $62, $64, $66 (96, 98, 100, 102)
every 8 game ticks, creating a 4-frame animation over 32 ticks.

From Tile_Layout_TS1 (Plains tileset), TILEA_QBLOCKCOIN ($63) uses patterns:
  - Upper left:  $98
  - Lower left:  $99
  - Upper right: $9A
  - Lower right: $9B

These patterns are in the PPU $0800-$0FFF range (second half of BG patterns).
Pattern $98 = tile index 24 ($18) within the 64-tile CHR bank.

The question block is a 16x16 tile composed of four 8x8 patterns:
  [UL $98] [UR $9A]
  [LL $99] [LR $9B]

Each CHR bank contains slightly different versions of these tiles,
creating the shimmer effect as the banks cycle.
"""

from PIL import Image
import os

# CHR banks used for the animation (in order: frame 0, 1, 2, 3)
CHR_BANKS = [96, 98, 100, 102]  # PT2_Anim: $60, $62, $64, $66

# Pattern indices within the bank (offset from $80)
# Pattern $98 = index $18 (24), $99 = $19 (25), $9A = $1A (26), $9B = $1B (27)
TILE_INDICES = {
    'UL': 0x18,  # Upper-left ($98 - $80)
    'LL': 0x19,  # Lower-left ($99 - $80)
    'UR': 0x1A,  # Upper-right ($9A - $80)
    'LR': 0x1B,  # Lower-right ($9B - $80)
}

# NES tile layout in PCX: 16 tiles per row, each tile 8x8
TILE_SIZE = 8
TILES_PER_ROW = 16

# NES color palette for question blocks (palette 1 typically)
# Indices: 0=background/transparent, 1=dark, 2=medium, 3=light
# The actual colors are taken from the NES palette based on the tileset
# For Plains, palette 1 for tiles $80-$BF is typically orange/yellow
QBLOCK_PALETTE = {
    0: (0, 0, 0, 0),           # transparent/background
    1: (0x00, 0x00, 0x00, 255),  # black (outline)
    2: (0xE4, 0x70, 0x18, 255),  # orange (main color)
    3: (0xFC, 0xE4, 0xA0, 255),  # light yellow/tan (highlight)
}

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

def compose_16x16_tile(img, tile_indices):
    """Compose a 16x16 tile from four 8x8 tiles."""
    ul = get_tile_pixels(img, tile_indices['UL'])
    ll = get_tile_pixels(img, tile_indices['LL'])
    ur = get_tile_pixels(img, tile_indices['UR'])
    lr = get_tile_pixels(img, tile_indices['LR'])
    
    # Combine: [UL][UR] over [LL][LR]
    result = []
    for row in ul:
        result.append(row + ur[ul.index(row) if row in ul else 0])
    for i, row in enumerate(ll):
        result.append(row + lr[i])
    
    # Fix: properly combine rows
    result = []
    for y in range(8):
        result.append(ul[y] + ur[y])
    for y in range(8):
        result.append(ll[y] + lr[y])
    
    return result

def save_16x16_tile(pixels, filename, palette):
    """Save a 16x16 tile as PNG with the given palette."""
    out = Image.new('RGBA', (16, 16))
    for y in range(16):
        for x in range(16):
            out.putpixel((x, y), palette[pixels[y][x]])
    out.save(filename)

def main():
    chr_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(chr_dir, 'question_block')
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print("QUESTION BLOCK ANIMATION EXTRACTION")
    print("="*60)
    print(f"\nCHR Banks: {CHR_BANKS}")
    print(f"Pattern indices: UL={TILE_INDICES['UL']}, LL={TILE_INDICES['LL']}, UR={TILE_INDICES['UR']}, LR={TILE_INDICES['LR']}")
    
    for frame_idx, bank_num in enumerate(CHR_BANKS):
        chr_filename = f'chr{bank_num:03d}.pcx'
        chr_path = os.path.join(chr_dir, chr_filename)
        
        if not os.path.exists(chr_path):
            print(f"\nERROR: {chr_filename} not found!")
            continue
        
        img = Image.open(chr_path)
        print(f"\nFrame {frame_idx} ({chr_filename}):")
        print(f"  Image size: {img.size}, mode: {img.mode}")
        
        # Extract and compose the 16x16 question block tile
        pixels = compose_16x16_tile(img, TILE_INDICES)
        
        # Show ASCII representation
        ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}
        print("  ASCII preview:")
        for row in pixels:
            print('    ' + ''.join(ASCII_MAP.get(p, '?') for p in row))
        
        # Save PNG
        output_file = os.path.join(output_dir, f'question_frame_{frame_idx}.png')
        save_16x16_tile(pixels, output_file, QBLOCK_PALETTE)
        print(f"  Saved: {output_file}")
    
    print("\n" + "="*60)
    print("ANIMATION TIMING (from prg030.asm):")
    print("="*60)
    print("""
Counter_1 AND #$18 gives values 0, 8, 16, 24
LSR A three times gives 0, 1, 2, 3
Each frame lasts 8 ticks (133ms at 60fps)
Full cycle: 32 ticks (533ms)

Frame sequence: chr096 -> chr098 -> chr100 -> chr102 -> repeat
""")

if __name__ == '__main__':
    main()
