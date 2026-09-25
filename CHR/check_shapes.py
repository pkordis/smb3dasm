#!/usr/bin/env python3
"""
Check coin sprite dimensions (8x8 vs 8x16) and render with real NES palette colours.
"""
from PIL import Image
import os

CHR_DIR = os.path.dirname(os.path.abspath(__file__))

# NES palette for SPR_PAL3 — coin sprite in plains levels
# Index 0 = transparent, 1 = black outline, 2 = orange/gold, 3 = white highlight
NES_PAL3_COIN = {
    0: (0,   0,   0,   0),
    1: (0,   0,   0,   255),
    2: (252, 160, 68,  255),
    3: (252, 252, 252, 255),
}

# NES palette for score popup (palette index 1 in the score draw code)
# Index 0 = transparent, 1/2/3 = progressively lighter text
NES_PAL1_SCORE = {
    0: (0,   0,   0,   0),
    1: (0,   0,   0,   255),
    2: (80,  80,  80,  255),
    3: (252, 252, 252, 255),
}


def get_tile(img, idx):
    col = idx % 16
    row = idx // 16
    return [[img.getpixel((col * 8 + x, row * 8 + y)) for x in range(8)]
            for y in range(8)]


def render_stack(tile_rows, palette, scale=8):
    """Render a list of 8-row tile grids stacked vertically."""
    all_rows = []
    for t in tile_rows:
        all_rows.extend(t)
    out = Image.new('RGBA', (8 * scale, len(all_rows) * scale))
    for y, row in enumerate(all_rows):
        for x, idx in enumerate(row):
            c = palette[idx]
            for sy in range(scale):
                for sx in range(scale):
                    out.putpixel((x * scale + sx, y * scale + sy), c)
    return out


def render_hstack(tile_grids, palette, scale=8):
    """Render a list of 8×8 grids side-by-side horizontally."""
    h = 8 * scale
    w = 8 * scale * len(tile_grids)
    out = Image.new('RGBA', (w, h))
    for i, grid in enumerate(tile_grids):
        for y, row in enumerate(grid):
            for x, idx in enumerate(row):
                c = palette[idx]
                for sy in range(scale):
                    for sx in range(scale):
                        out.putpixel((i * 8 * scale + x * scale + sx,
                                      y * scale + sy), c)
    return out


img = Image.open(os.path.join(CHR_DIR, 'chr004.pcx'))

# Coin tiles: local indices 8+9, 12+13, 14+15 (top+bottom of each 8x16 pair)
t8  = get_tile(img, 8)
t9  = get_tile(img, 9)
t12 = get_tile(img, 12)
t13 = get_tile(img, 13)
t14 = get_tile(img, 14)
t15 = get_tile(img, 15)

# Render as 8x16 (both tiles stacked)
render_stack([t8,  t9],  NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_49_8x16.png'))
render_stack([t12, t13], NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_4D_8x16.png'))
render_stack([t14, t15], NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_4F_8x16.png'))
print('coin 8x16 renders saved')

# Render as 8x8 (bottom tile only — what we extracted previously)
render_stack([t9],  NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_49_8x8.png'))
render_stack([t13], NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_4D_8x8.png'))
render_stack([t15], NES_PAL3_COIN).save(os.path.join(CHR_DIR, 'check_coin_4F_8x8.png'))
print('coin 8x8 renders saved')

# All 3 coin frames side by side for easy comparison (8x16 versions)
strip_8x16 = Image.new('RGBA', (8 * 8 * 3, 16 * 8), (20, 20, 20, 255))
for i, (top, bot) in enumerate([(t8, t9), (t14, t15), (t12, t13)]):
    frame = render_stack([top, bot], NES_PAL3_COIN)
    strip_8x16.paste(frame, (i * 8 * 8, 0), frame)
strip_8x16.save(os.path.join(CHR_DIR, 'check_coin_all_8x16.png'))
print('coin all-frames 8x16 strip saved')

# Score tiles
t25 = get_tile(img, 25)
t27 = get_tile(img, 27)
t33 = get_tile(img, 33)
t35 = get_tile(img, 35)
t41 = get_tile(img, 41)
t43 = get_tile(img, 43)
t45 = get_tile(img, 45)
t47 = get_tile(img, 47)

# 100pt = tile_5B (local 27) left + tile_69 (local 41) right
render_hstack([t27, t41], NES_PAL1_SCORE).save(os.path.join(CHR_DIR, 'check_score_100.png'))

# All score values strip
score_combos = [
    ([],    [t27]),  # 10
    ([],    [t35]),  # 20
    ([],    [t43]),  # 40
    ([],    [t45]),  # 80
    ([t27], [t41]),  # 100
    ([t35], [t41]),  # 200
    ([t43], [t41]),  # 400
    ([t45], [t41]),  # 800
    ([t27], [t25]),  # 1000
    ([t35], [t25]),  # 2000
    ([t43], [t25]),  # 4000
    ([t45], [t25]),  # 8000
    ([t33], [t47]),  # 1UP
]
score_strip = Image.new('RGBA', (16 * 8, 8 * 8 * len(score_combos)), (20, 20, 20, 255))
for i, (left_tiles, right_tiles) in enumerate(score_combos):
    tiles = left_tiles + right_tiles
    if len(tiles) == 1:
        frame = render_hstack([tiles[0], [[0]*8]*8], NES_PAL1_SCORE)
    else:
        frame = render_hstack(tiles, NES_PAL1_SCORE)
    score_strip.paste(frame, (0, i * 8 * 8), frame)
score_strip.save(os.path.join(CHR_DIR, 'check_score_all.png'))
print('score renders saved')
print('Done.')
