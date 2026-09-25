"""
Extract all small Mario frames from chr083.pcx using the correct tile pairing.

CONFIRMED: tile ID N in the frame table = bottom half of 8x16 sprite.
           tile ID N-1 = top half.
           (Even tile = top, odd tile = bottom in each 8x16 pair.)

Frame table (SPPF_Table, bytes[3] and bytes[4] = bottom-left and bottom-middle slots):
  PF3E (still/walk-1): left=$05->top=$04,bot=$05  right=$07->top=$06,bot=$07
  PF3F (walk-2):       left=$01->top=$00,bot=$01  right=$03->top=$02,bot=$03
  PF40 (jump/fall):    left=$19->top=$18,bot=$19  right=$1B->top=$1A,bot=$1B
  PF41 (skid):         left=$21->top=$20,bot=$21  right=$23->top=$22,bot=$23
  PF4C (run-1):        left=$31->top=$30,bot=$31  right=$33->top=$32,bot=$33
  PF4D (run-2):        left=$35->top=$34,bot=$35  right=$37->top=$36,bot=$37
  PF4E (fast-jump):    left=$0F->top=$0E,bot=$0F  right=$3F->top=$3E,bot=$3F

All sprites face LEFT in the CHR (player faces right via SPR_HFLIP attribute).
Output: 16x16 PNGs (actual sprite size) — no padding needed.
The project's ShrunkAnimator will use QUAD_HEIGHT=1.0 (16px) not 2.0 (32px).
"""

from pathlib import Path
import struct, zlib

PALETTE = [
    (0,    0,    0,    0),
    (0x7C, 0x30, 0x00, 255),
    (0xD8, 0x28, 0x00, 255),
    (0xFC, 0xBC, 0xB0, 255),
]

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
    return w, h, [raw[y * bpl : y * bpl + w] for y in range(h)]

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
    print(f'  {Path(path).name}')

def get_tile(px, w, tid):
    tpr = w // 8
    tr, tc = tid // tpr, tid % tpr
    if tr * 8 + 7 >= len(px):
        return [[0]*8 for _ in range(8)]
    return [px[tr*8+y][tc*8:tc*8+8] for y in range(8)]

def get_8x16(px, w, frame_tid):
    """8x16 sprite: top = frame_tid-1, bottom = frame_tid (confirmed mode C)."""
    top = get_tile(px, w, frame_tid - 1)
    bot = get_tile(px, w, frame_tid)
    return top + bot

def assemble_frame(px, w, left_tid, right_tid):
    """16x16 RGBA from two 8x16 slots."""
    L = get_8x16(px, w, left_tid)
    R = get_8x16(px, w, right_tid)
    return [[PALETTE[L[y][x]] for x in range(8)] +
            [PALETTE[R[y][x]] for x in range(8)]
            for y in range(16)]

def scale(rows, n):
    return [[px for px in row for _ in range(n)] for row in rows for _ in range(n)]

CHR  = r'C:\Users\pkordis\Projects\smb3dasm\CHR\chr083.pcx'
OUT  = Path(r'C:\Users\pkordis\Projects\smb3dasm\CHR\small_mario\final')
OUT.mkdir(exist_ok=True)

# Output also goes directly into the project sprites folder
SPRITES = Path(r'C:\Users\pkordis\Projects\super-mario-bros-3\src\main\resources\sprites\player\mario\level\shrunk')

w, h, px = load_pcx(CHR)
print(f'chr083.pcx: {w}x{h}')

# (output_name, left_tid, right_tid)
# left_tid/right_tid are the OAM tile IDs from SPPF_Table bytes[3]/[4]
FRAMES = [
    ('still',      0x05, 0x07),  # PF3E — also walk frame 1
    ('walking',    0x01, 0x03),  # PF3F — walk frame 2 (alternates with still/walk1)
    ('jumping',    0x19, 0x1B),  # PF40
    ('rapid_turn', 0x21, 0x23),  # PF41 skid
    ('running_1',  0x31, 0x33),  # PF4C
    ('running_2',  0x35, 0x37),  # PF4D
    ('flying',     0x0F, 0x3F),  # PF4E fast-jump (full P-meter)
]

print('\n--- Preview PNGs (8x scale, in final/) ---')
for name, lt, rt in FRAMES:
    rgba = assemble_frame(px, w, lt, rt)
    write_png(str(OUT / f'{name}_8x.png'), scale(rgba, 8))

print('\n--- Production PNGs (16x16, written to both final/ and sprites/shrunk/) ---')
for name, lt, rt in FRAMES:
    rgba = assemble_frame(px, w, lt, rt)
    out_final  = str(OUT / f'{name}.png')
    out_sprite = str(SPRITES / f'{name}.png')
    write_png(out_final, rgba)
    write_png(out_sprite, rgba)

print('\nDone.')
print(f'Preview: {OUT}')
print(f'Sprites: {SPRITES}')
