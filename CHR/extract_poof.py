"""
Extract poof animation tiles from the SMB3 CHR data.

CORRECTED ANALYSIS:
Each chr###.pcx file = 128x32 pixels = 64 tiles = 1KB.
So chr###.pcx IS 1KB bank ### directly!

During gameplay, PatTable_BankSel[3] = $04 for the sprite bank at PPU $1400-$17FF.
This means chr004.pcx contains the tiles mapped to PPU tile indices $40-$7F.

In 8x16 sprite mode:
  - Tile $41: bit 0=1 (use PT at $1000), pair index = $40/$41
  - Tile $40 at PPU address $1000 + $40*16 = $1400
  - The MMC3 maps $1400-$17FF from PatTable_BankSel[3] = bank $04 = chr004.pcx

Within chr004.pcx (64 tiles, 0-63):
  - PPU tile $40 = chr004 tile 0
  - PPU tile $41 = chr004 tile 1
  - PPU tile $42 = chr004 tile 2
  - ...
  - PPU tile $47 = chr004 tile 7

Poof_Patterns: .byte $47, $45, $43, $41
  BrickBust_HEn >> 3 indexes this table.
  HEn starts at $17 (23) for brick thaw, $1F (31) for cannon.
  For $17: frames cycle 2->1->0 as HEn decrements.
  For $1F: frames cycle 3->2->1->0.

Animation sequence (as HEn decrements):
  HEn 24-31 (>>3=3): Poof_Patterns[3] = $41 (Frame 1 - initial small poof)
  HEn 16-23 (>>3=2): Poof_Patterns[2] = $43 (Frame 2 - growing)
  HEn  8-15 (>>3=1): Poof_Patterns[1] = $45 (Frame 3 - large)
  HEn  0-7  (>>3=0): Poof_Patterns[0] = $47 (Frame 4 - dissipating/final)
"""

from PIL import Image
import os

# Open the correct CHR file
chr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chr004.pcx')
img = Image.open(chr_path)
print(f"chr004.pcx: Size={img.size}, Mode={img.mode}")

if img.mode == 'P':
    pal = img.getpalette()
    print(f"PCX palette (first 4 entries - raw NES greyscale encoding):")
    for i in range(4):
        r, g, b = pal[i*3], pal[i*3+1], pal[i*3+2]
        print(f"  Color {i}: #{r:02X}{g:02X}{b:02X}")

# NES tile layout in PCX: 16 tiles per row, each tile 8x8
TILE_SIZE = 8
TILES_PER_ROW = img.size[0] // TILE_SIZE  # 16

print(f"\nTiles per row: {TILES_PER_ROW}")
print(f"Total tiles: {TILES_PER_ROW * (img.size[1] // TILE_SIZE)}")

# NES color palette for poof sprites (as specified by user):
# 0 = transparent, 1 = black #000000, 2 = #D8A060, 3 = #E47018
POOF_PALETTE = {
    0: (0, 0, 0, 0),       # transparent
    1: (0x00, 0x00, 0x00, 255),  # black
    2: (0xD8, 0xA0, 0x60, 255),  # tan/brown
    3: (0xE4, 0x70, 0x18, 255),  # orange
}

# ASCII representation for colors
ASCII_MAP = {0: '.', 1: '#', 2: 'o', 3: '@'}

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

def print_tile_ascii(pixels, label):
    """Print tile as ASCII art."""
    print(f"  {label}:")
    for row in pixels:
        print('    ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

def save_8x16_sprite(img, top_index, bottom_index, filename, palette):
    """Save an 8x16 sprite (two tiles stacked) as PNG."""
    out = Image.new('RGBA', (8, 16))
    top_pixels = get_tile_pixels(img, top_index)
    bottom_pixels = get_tile_pixels(img, bottom_index)
    
    for y in range(8):
        for x in range(8):
            out.putpixel((x, y), palette[top_pixels[y][x]])
    for y in range(8):
        for x in range(8):
            out.putpixel((x, y + 8), palette[bottom_pixels[y][x]])
    
    out.save(filename)
    print(f"  Saved: {filename}")

# Extract and display tiles 0-7 from chr004.pcx
print("\n" + "="*60)
print("POOF TILES (from chr004.pcx, 1KB bank $04)")
print("PPU tile indices $40-$47 in the sprite pattern table")
print("="*60)

# Poof_Patterns: $47, $45, $43, $41 (indexed by BrickBust_HEn >> 3)
# Animation plays from high HEn to low, so sequence is: $41 -> $43 -> $45 -> $47
poof_frames = [
    ("$41 (Frame 1 - initial small poof, HEn=24-31)", 0, 1),
    ("$43 (Frame 2 - growing, HEn=16-23)", 2, 3),
    ("$45 (Frame 3 - large poof, HEn=8-15)", 4, 5),
    ("$47 (Frame 4 - dissipating/final, HEn=0-7)", 6, 7),
]

output_dir = os.path.dirname(os.path.abspath(__file__))

for label, top_idx, bottom_idx in poof_frames:
    top_pixels = get_tile_pixels(img, top_idx)
    bottom_pixels = get_tile_pixels(img, bottom_idx)
    
    ppu_top = 0x40 + top_idx
    ppu_bottom = 0x40 + bottom_idx
    
    print(f"\n{'='*50}")
    print(f"Pattern {label}")
    print(f"  PPU tiles ${ppu_top:02X} (top) / ${ppu_bottom:02X} (bottom)")
    print(f"  chr004.pcx tile indices: {top_idx} (top), {bottom_idx} (bottom)")
    print_tile_ascii(top_pixels, f"Tile ${ppu_top:02X} (top half)")
    print()
    print_tile_ascii(bottom_pixels, f"Tile ${ppu_bottom:02X} (bottom half)")
    
    # Combined 8x16 view
    print(f"\n  Combined 8x16 sprite (as rendered in-game, single sprite):")
    for row in top_pixels:
        print('    ' + ''.join(ASCII_MAP.get(p, '?') for p in row))
    for row in bottom_pixels:
        print('    ' + ''.join(ASCII_MAP.get(p, '?') for p in row))

# Save PNGs with correct palette
print("\n" + "="*60)
print("SAVING PNG FILES to ~/Projects/smb3dasm/CHR/")
print("="*60)

frame_names = ['poof_frame1_41', 'poof_frame2_43', 'poof_frame3_45', 'poof_frame4_47']

for i, (label, top_idx, bottom_idx) in enumerate(poof_frames):
    filename = os.path.join(output_dir, f"{frame_names[i]}.png")
    save_8x16_sprite(img, top_idx, bottom_idx, filename, POOF_PALETTE)

# Also save individual 8x8 tiles
print("\n  Individual 8x8 tiles:")
for tile_idx in range(8):
    pixels = get_tile_pixels(img, tile_idx)
    out = Image.new('RGBA', (8, 8))
    for y in range(8):
        for x in range(8):
            out.putpixel((x, y), POOF_PALETTE[pixels[y][x]])
    ppu_id = 0x40 + tile_idx
    filename = os.path.join(output_dir, f"poof_tile_{ppu_id:02X}.png")
    out.save(filename)
    print(f"    Saved: {filename} (PPU tile ${ppu_id:02X})")

print("\n" + "="*60)
print("HOW THE POOF RENDERS IN-GAME:")
print("="*60)
print("""
The poof is drawn as a 16x16 effect using TWO 8x16 sprites side by side:
  - Left sprite: pattern from Poof_Patterns[X], attributes = SPR_PAL1 | periodic_VFLIP
  - Right sprite: SAME pattern, attributes = SPR_PAL1 | HFLIP | inverted_VFLIP

The HFLIP on the right sprite mirrors the left half horizontally, creating
a symmetrical 16x16 poof effect from just one 8x16 tile.

The VFLIP toggles every 8 frames (Level_NoStopCnt>>3, bit 7 rotated in)
creating a shimmering rotation effect.

Palette: SPR_PAL1 = sprite palette 1 (the second sprite palette)
In most levels this maps to: 0=transparent, 1=black, 2=tan/brown, 3=orange

Animation duration:
  - Brick thaw poof: HEn starts at $17 (23 frames total, ~3 frame changes)
  - Cannon poof: HEn starts at $1F (31 frames total, all 4 frames used)
  - Each animation frame lasts 8 ticks (HEn>>3 changes every 8 decrements)
""")
