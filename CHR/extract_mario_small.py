"""
Extract small Mario frames from chr083.pcx.

OAM layout per Player_Draw (prg029.asm):
  6 sprite slots in a 3-col x 2-row grid, each sprite 8x16px.
  For small Mario, only 2 bottom-row slots are visible:
    Bottom-Left  (X+0,  Y+16) = bytes[3]
    Bottom-Middle(X+8,  Y+16) = bytes[4]
    Bottom-Right          = bytes[5] = $F1 (invisible)
    Top row (bytes 0-2)   = all $F1

Frames:
  PF3E (still / walk-1): bytes $F1,$F1,$F1, $05,$07,$F1
  PF3F (walk-2):         bytes $F1,$F1,$F1, $01,$03,$F1
  PF40 (jump/fall):      bytes $F1,$F1,$F1, $19,$1B,$F1
  PF41 (skid):           bytes $F1,$F1,$F1, $21,$23,$F1
  PF4C (run-1):          bytes $F1,$F1,$F1, $31,$33,$F1
  PF4D (run-2):          bytes $F1,$F1,$F1, $35,$37,$F1
  PF4E (fast-jump):      bytes $F1,$F1,$F1, $0F,$3F,$F1

In 8x16 sprite mode, tile ID N uses:
  top 8px  = CHR tile N
  bottom 8px = CHR tile N+1

The full rendered size is 16 wide x 16 tall (2 slots x 1 visible row).
We produce the sprite at 16x16, plus a 16x32 version with empty top half
(transparent) matching the project's render slot.

NES palette for small Mario (suit palette 0, red Mario):
  index 0 -> transparent
  index 1 -> #7C3000  dark brown outline
  index 2 -> #D82800  red (hat/shirt)
  index 3 -> #FCBCB0  skin/tan
"""

from pathlib import Path
import struct, zlib

PALETTE = [
    (0,    0,    0,    0),     # 0 transparent
    (0x7C, 0x30, 0x00, 255),  # 1 dark outline
    (0xD8, 0x28, 0x00, 255),  # 2 red
    (0xFC, 0xBC, 0xB0, 255),  # 3 skin
]

# --------------------------------------------------------------------------
def load_pcx(path):
    data = Path(path).read_bytes()
    xmax = struct.unpack_from('<H', data, 8)[0]
    ymax = struct.unpack_from('<H', data, 10)[0]
    bpl  = struct.unpack_from('<H', data, 66)[0]
    w, h = xmax + 1, ymax + 1
    raw, i = [], 128
    while len(raw) < h * bpl + 100 and i < len(data) - 769:
        b = data[i]; i += 1
        if (b & 0xC0) == 0xC0:
            cnt = b & 0x3F; v = data[i]; i += 1
            raw.extend([v] * cnt)
        else:
            raw.append(b)
    px = [raw[y * bpl : y * bpl + w] for y in range(h)]
    return w, h, px

def write_png(path, rows):
    h, w = len(rows), len(rows[0])
    ihdr = struct.pack('>II', w, h) + bytes([8, 6, 0, 0, 0])
    raw = b''.join(b'\x00' + bytes([c for px in row for c in px]) for row in rows)
    def ck(tag, d):
        c = tag + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    Path(path).write_bytes(
        b'\x89PNG\r\n\x1a\n' + ck(b'IHDR', ihdr) +
        ck(b'IDAT', zlib.compress(raw, 9)) + ck(b'IEND', b''))
    print(f'  {path}')

def get_tile(px, w, tid):
    """8x8 tile as list of 8 rows of 8 color-indices. Returns blank if out of range."""
    tpr = w // 8
    tr, tc = tid // tpr, tid % tpr
    if tr * 8 + 7 >= len(px):
        return [[0] * 8 for _ in range(8)]  # out of page -> transparent
    return [px[tr*8 + y][tc*8 : tc*8 + 8] for y in range(8)]

def get_8x16(px, w, tid):
    """8x16: tile tid (top) + tid+1 (bottom)."""
    return get_tile(px, w, tid) + get_tile(px, w, tid + 1)

def to_rgba(indices_rows):
    return [[PALETTE[v] for v in row] for row in indices_rows]

def scale(rows, n):
    return [
        [px for px in row for _ in range(n)]
        for row in rows for _ in range(n)
    ]

def make_frame_16x16(px, w, left_tid, right_tid):
    """16x16 RGBA: left 8x16 sprite | right 8x16 sprite."""
    L = get_8x16(px, w, left_tid)
    R = get_8x16(px, w, right_tid)
    return [[PALETTE[L[y][x]] for x in range(8)] +
            [PALETTE[R[y][x]] for x in range(8)]
            for y in range(16)]

def make_frame_16x32(px, w, left_tid, right_tid):
    """16x32 RGBA: transparent top-half + 16x16 sprite bottom-half.
    Matches the project's render slot (32px tall, sprite occupies bottom 16px)."""
    transparent_row = [(0, 0, 0, 0)] * 16
    top = [transparent_row[:] for _ in range(16)]
    bottom = make_frame_16x16(px, w, left_tid, right_tid)
    return top + bottom

# --------------------------------------------------------------------------
CHR  = r'C:\Users\pkordis\Projects\smb3dasm\CHR\chr083.pcx'
OUT  = Path(r'C:\Users\pkordis\Projects\smb3dasm\CHR\small_mario')
OUT.mkdir(exist_ok=True)

w, h, px = load_pcx(CHR)
print(f'chr083.pcx: {w}x{h}')

# Every small-Mario frame: (name, bottom-left tile, bottom-middle tile)
# Tile IDs from SPPF_Table bytes[3] and bytes[4]
FRAMES = [
    ('pf3e_still_walk1',  0x05, 0x07),
    ('pf3f_walk2',        0x01, 0x03),
    ('pf40_jump_fall',    0x19, 0x1B),
    ('pf41_skid',         0x21, 0x23),
    ('pf4c_run1',         0x31, 0x33),
    ('pf4d_run2',         0x35, 0x37),
    # PF4E tile $3F right: $3F+1 wraps to next page — clamp to blank bottom half
    ('pf4e_fast_jump',    0x0F, 0x3F),
]

print('\n--- Individual tiles (8x8, scaled 8x) ---')
# Dump every tile that appears in any small-Mario frame for reference
seen = set()
for _, lt, rt in FRAMES:
    for tid in [lt, lt+1, rt, rt+1]:
        if tid not in seen:
            seen.add(tid)
            tile_px = get_tile(px, w, tid)
            tile_rgba = to_rgba(tile_px)
            write_png(str(OUT / f'tile_{tid:02X}.png'), scale(tile_rgba, 8))

print('\n--- 16x16 frames (scaled 8x) ---')
for name, lt, rt in FRAMES:
    rgba = make_frame_16x16(px, w, lt, rt)
    write_png(str(OUT / f'{name}_16x16.png'), rgba)
    write_png(str(OUT / f'{name}_16x16_8x.png'), scale(rgba, 8))

print('\n--- 16x32 render-slot frames (scaled 8x) ---')
print('(transparent top half + sprite bottom half, matching project render slot)')
for name, lt, rt in FRAMES:
    rgba = make_frame_16x32(px, w, lt, rt)
    write_png(str(OUT / f'{name}_16x32.png'), rgba)
    write_png(str(OUT / f'{name}_16x32_8x.png'), scale(rgba, 8))

print('\nDone. Output in:', OUT)
