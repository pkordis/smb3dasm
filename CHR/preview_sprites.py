#!/usr/bin/env python3
"""Render all extracted coin and score sprites with visible colours for inspection."""
from PIL import Image
import os

TILE_SIZE = 8
TILES_PER_ROW = 16
CHR_DIR = os.path.dirname(os.path.abspath(__file__))

# Index 0 = dark bg (transparent in final assets), 1/2/3 = shades of white
COLOURS = {
    0: (30, 30, 30, 255),
    1: (80, 80, 80, 255),
    2: (180, 180, 180, 255),
    3: (255, 255, 255, 255),
}


def get_tile(img, idx):
    col = idx % TILES_PER_ROW
    row = idx // TILES_PER_ROW
    return [[img.getpixel((col * TILE_SIZE + x, row * TILE_SIZE + y))
             for x in range(TILE_SIZE)] for y in range(TILE_SIZE)]


def render_tile(pixels, scale=12):
    out = Image.new('RGBA', (TILE_SIZE * scale, TILE_SIZE * scale))
    for y, row in enumerate(pixels):
        for x, idx in enumerate(row):
            c = COLOURS.get(idx, (255, 0, 255, 255))
            for sy in range(scale):
                for sx in range(scale):
                    out.putpixel((x * scale + sx, y * scale + sy), c)
    return out


def render_two(left, right, scale=12):
    out = Image.new('RGBA', (TILE_SIZE * 2 * scale, TILE_SIZE * scale))
    out.paste(render_tile(left, scale), (0, 0))
    out.paste(render_tile(right, scale), (TILE_SIZE * scale, 0))
    return out


chr004 = Image.open(os.path.join(CHR_DIR, 'chr004.pcx'))
SCALE = 12

# --- coin ---
coin_specs = [
    (9,  'coin_frame0_front.png'),
    (15, 'coin_frame1_angled.png'),
    (13, 'coin_frame2_thin.png'),
]
for local, fname in coin_specs:
    render_tile(get_tile(chr004, local), SCALE).save(os.path.join(CHR_DIR, fname))
    print(f'  {fname}')

# frame 3 = frame 1 hflip
px1 = get_tile(chr004, 15)
px1_flip = [row[::-1] for row in px1]
render_tile(px1_flip, SCALE).save(os.path.join(CHR_DIR, 'coin_frame3_hflip.png'))
print('  coin_frame3_hflip.png')

# coin strip (4 frames side by side)
coin_strip = Image.new('RGBA', (TILE_SIZE * 4 * SCALE, TILE_SIZE * SCALE), (20, 20, 20, 255))
frames = [get_tile(chr004, 9), get_tile(chr004, 15), get_tile(chr004, 13), px1_flip]
for i, px in enumerate(frames):
    coin_strip.paste(render_tile(px, SCALE), (i * TILE_SIZE * SCALE, 0))
coin_strip.save(os.path.join(CHR_DIR, 'coin_all_frames.png'))
print('  coin_all_frames.png')

# --- score ---
score_specs = [
    (25, 0x59, 'score_tile_59_000.png'),
    (27, 0x5B, 'score_tile_5B_1.png'),
    (33, 0x61, 'score_tile_61_1UP_left.png'),
    (35, 0x63, 'score_tile_63_2.png'),
    (41, 0x69, 'score_tile_69_00.png'),
    (43, 0x6B, 'score_tile_6B_4.png'),
    (45, 0x6D, 'score_tile_6D_8.png'),
    (47, 0x6F, 'score_tile_6F_1UP_right.png'),
]
score_px = {}
for local, patid, fname in score_specs:
    px = get_tile(chr004, local)
    score_px[patid] = px
    render_tile(px, SCALE).save(os.path.join(CHR_DIR, fname))
    print(f'  {fname}')

# 100pt composite
render_two(score_px[0x5B], score_px[0x69], SCALE).save(
    os.path.join(CHR_DIR, 'score_100pt.png'))
print('  score_100pt.png')

# all score values strip
blank = [[0] * TILE_SIZE for _ in range(TILE_SIZE)]
combos = [
    (' 10', blank,           score_px[0x5B]),
    (' 20', blank,           score_px[0x63]),
    (' 40', blank,           score_px[0x6B]),
    (' 80', blank,           score_px[0x6D]),
    ('100', score_px[0x5B],  score_px[0x69]),
    ('200', score_px[0x63],  score_px[0x69]),
    ('400', score_px[0x6B],  score_px[0x69]),
    ('800', score_px[0x6D],  score_px[0x69]),
    ('1k+', score_px[0x5B],  score_px[0x59]),
    ('2k+', score_px[0x63],  score_px[0x59]),
    ('4k+', score_px[0x6B],  score_px[0x59]),
    ('8k+', score_px[0x6D],  score_px[0x59]),
    ('1UP', score_px[0x61],  score_px[0x6F]),
]
strip_h = TILE_SIZE * SCALE * len(combos)
strip_w = TILE_SIZE * 2 * SCALE
strip = Image.new('RGBA', (strip_w, strip_h), (20, 20, 20, 255))
for i, (label, left, right) in enumerate(combos):
    strip.paste(render_two(left, right, SCALE), (0, i * TILE_SIZE * SCALE))
strip.save(os.path.join(CHR_DIR, 'score_all.png'))
print('  score_all.png')
print('Done.')
