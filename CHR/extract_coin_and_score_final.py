#!/usr/bin/env python3
"""
Definitive extraction of coin and score popup sprites.

COIN — 8x16 sprite (two 8x8 tiles stacked, top+bottom).
  Pattern IDs from CoinPUp_Patterns (prg007.asm):  0x49, 0x4F, 0x4D, 0x4F
  In 8x16 mode bit 0 is ignored: $49 -> top=$48 (local 8) + bot=$49 (local 9)
  All from chr004, BankSel+3=4 (set every frame by Player_DoGameplay, prg008.asm).

  Animation: step 0 ($49) -> step 1 ($4F) -> step 2 ($4D) -> step 3 ($4F hflip) -> repeat
  SPR_PAL3 throughout. Step 3 is same tile as step 1, H-flipped via attribute bit.

SCORE — 8x8 per tile, 1 or 2 tiles side-by-side (8x8 or 16x8 total).
  Score_PatternLeft/Right (prg007.asm line 2121-2122), all IDs from chr004.
  Score attribute: palette 1 (prg007.asm Score_SetAttribute).
"""

import os
from PIL import Image

CHR_DIR   = os.path.dirname(os.path.abspath(__file__))
# CHR_DIR = C:\Users\pkordis\Projects\smb3dasm\CHR
# Go up two levels (CHR -> smb3dasm -> Projects) then into super-mario-bros-3
PROJECTS_DIR = os.path.dirname(os.path.dirname(CHR_DIR))
PROJECT_ROOT = os.path.join(PROJECTS_DIR, 'super-mario-bros-3')
COIN_DIR  = os.path.join(PROJECT_ROOT, 'src', 'main', 'resources', 'sprites', 'object', 'coin')
SCORE_DIR = os.path.join(PROJECT_ROOT, 'src', 'main', 'resources', 'sprites', 'object', 'score')
os.makedirs(COIN_DIR,  exist_ok=True)
os.makedirs(SCORE_DIR, exist_ok=True)

# --- NES palettes ---
# SPR_PAL3 for coin in plains: transparent / black outline / orange-gold / white highlight
COIN_PAL = {
    0: (0,   0,   0,   0),
    1: (0,   0,   0,   255),
    2: (252, 160, 68,  255),
    3: (252, 252, 252, 255),
}
# PAL1 for score text: transparent / black / mid-grey / white
SCORE_PAL = {
    0: (0,   0,   0,   0),
    1: (0,   0,   0,   255),
    2: (80,  80,  80,  255),
    3: (252, 252, 252, 255),
}


def get_tile(img, local):
    col, row = local % 16, local // 16
    return [[img.getpixel((col * 8 + x, row * 8 + y)) for x in range(8)]
            for y in range(8)]


def hflip(grid):
    return [row[::-1] for row in grid]


def render(tiles, palette, *, hflip_all=False):
    """Render a list of 8x8 grids stacked vertically into one RGBA image."""
    rows = []
    for t in tiles:
        rows.extend(hflip(t) if hflip_all else t)
    out = Image.new('RGBA', (8, len(rows)))
    for y, row in enumerate(rows):
        for x, idx in enumerate(row):
            out.putpixel((x, y), palette[idx])
    return out


def render_wide(left_tiles, right_tiles, palette, *, hflip_all=False):
    """Render two columns of stacked 8x8 grids side-by-side."""
    left_rows  = []
    right_rows = []
    for t in left_tiles:
        left_rows.extend(hflip(t) if hflip_all else t)
    for t in right_tiles:
        right_rows.extend(hflip(t) if hflip_all else t)
    h = max(len(left_rows), len(right_rows))
    out = Image.new('RGBA', (16, h))
    for y, row in enumerate(left_rows):
        for x, idx in enumerate(row):
            out.putpixel((x, y), palette[idx])
    for y, row in enumerate(right_rows):
        for x, idx in enumerate(row):
            out.putpixel((8 + x, y), palette[idx])
    return out


def save(img, *paths, scale=1):
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    for p in paths:
        img.save(p)
        print(f'  -> {os.path.relpath(p, CHR_DIR)}')


img = Image.open(os.path.join(CHR_DIR, 'chr004.pcx'))

# -----------------------------------------------------------------------
print('COIN  8x16 sprites')
# Each pattern: top tile = patternID & 0xFE (even), bot = patternID | 0x01 (odd)
# local = patternID - 0x40
t_coin_top = {
    0x49: get_tile(img, 8),   # $48 local 8
    0x4D: get_tile(img, 12),  # $4C local 12
    0x4F: get_tile(img, 14),  # $4E local 14
}
t_coin_bot = {
    0x49: get_tile(img, 9),   # $49 local 9
    0x4D: get_tile(img, 13),  # $4D local 13
    0x4F: get_tile(img, 15),  # $4F local 15
}

for step, (pat, flip, fname) in enumerate([
    (0x49, False, 'frame_0.png'),
    (0x4F, False, 'frame_1.png'),
    (0x4D, False, 'frame_2.png'),
    (0x4F, True,  'frame_3_hflip.png'),
]):
    tiles = [t_coin_top[pat], t_coin_bot[pat]]
    img_out = render(tiles, COIN_PAL, hflip_all=flip)
    save(img_out, os.path.join(COIN_DIR, fname))

print('  coin: 4 frames saved (8x16 each)')

# -----------------------------------------------------------------------
print('SCORE  8x8 individual tiles')

score_tile_map = {
    0x59: get_tile(img, 25),
    0x5B: get_tile(img, 27),
    0x61: get_tile(img, 33),
    0x63: get_tile(img, 35),
    0x69: get_tile(img, 41),
    0x6B: get_tile(img, 43),
    0x6D: get_tile(img, 45),
    0x6F: get_tile(img, 47),
}

tile_fnames = {
    0x59: 'tile_59.png',
    0x5B: 'tile_5B.png',
    0x61: 'tile_61.png',
    0x63: 'tile_63.png',
    0x69: 'tile_69.png',
    0x6B: 'tile_6B.png',
    0x6D: 'tile_6D.png',
    0x6F: 'tile_6F.png',
}
for pat, fname in tile_fnames.items():
    save(render([score_tile_map[pat]], SCORE_PAL), os.path.join(SCORE_DIR, fname))

print('SCORE  composite sprites (16x8)')
blank = [[0] * 8 for _ in range(8)]
composites = [
    ('score_010.png',  None,   0x5B),
    ('score_020.png',  None,   0x63),
    ('score_040.png',  None,   0x6B),
    ('score_080.png',  None,   0x6D),
    ('score_100.png',  0x5B,   0x69),
    ('score_200.png',  0x63,   0x69),
    ('score_400.png',  0x6B,   0x69),
    ('score_800.png',  0x6D,   0x69),
    ('score_1000.png', 0x5B,   0x59),
    ('score_2000.png', 0x63,   0x59),
    ('score_4000.png', 0x6B,   0x59),
    ('score_8000.png', 0x6D,   0x59),
    ('score_1up.png',  0x61,   0x6F),
]
for fname, left_pat, right_pat in composites:
    left  = [score_tile_map[left_pat]]  if left_pat  else [blank]
    right = [score_tile_map[right_pat]] if right_pat else [blank]
    save(render_wide(left, right, SCORE_PAL), os.path.join(SCORE_DIR, fname))

print('Done.')
