"""
Diagnose the tile ordering in chr083.pcx by trying all combinations
of top/bottom assignment for PF3E (tiles $05, $07).

We know from all_marios_shrunk.png what small Mario looks like.
Try: sequential (N=top, N+1=bottom), swapped (N+1=top, N=bottom),
and also try N-1=top, N=bottom (since all small tile IDs are odd).
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

def get_tile(px, w, tid):
    tpr = w // 8
    tr, tc = tid // tpr, tid % tpr
    if tr * 8 + 7 >= len(px):
        return [[0]*8 for _ in range(8)]
    return [px[tr*8+y][tc*8:tc*8+8] for y in range(8)]

def tile_to_rgba(t):
    return [[PALETTE[v] for v in row] for row in t]

def scale(rows, n):
    return [[px for px in row for _ in range(n)] for row in rows for _ in range(n)]

def side_by_side(left_rows, right_rows):
    return [l + r for l, r in zip(left_rows, right_rows)]

CHR = r'C:\Users\pkordis\Projects\smb3dasm\CHR\chr083.pcx'
OUT = Path(r'C:\Users\pkordis\Projects\smb3dasm\CHR\small_mario\diag')
OUT.mkdir(exist_ok=True)

w, h, px = load_pcx(CHR)

# Print tile layout info
tpr = w // 8
print(f'Sheet: {w}x{h}, tiles_per_row={tpr}, total tile rows={h//8}')
print(f'Total tiles: {tpr * (h//8)}')
print()

# Dump all 64 tiles as a grid overview
all_rgba = []
for tr in range(h // 8):
    row_rgba = None
    for tc in range(tpr):
        tid = tr * tpr + tc
        t = tile_to_rgba(get_tile(px, w, tid))
        t_scaled = scale(t, 4)
        if row_rgba is None:
            row_rgba = t_scaled
        else:
            row_rgba = [a + b for a, b in zip(row_rgba, t_scaled)]
    all_rgba.extend(row_rgba)
write_png(str(OUT / 'all_tiles_4x.png'), all_rgba)
print('Wrote all_tiles_4x.png')

# For PF3E: left slot = tile $05, right slot = $07
# Try all pairing modes for the left slot (tile $05):
# Mode A: top=$05, bot=$06  (sequential, N=top)
# Mode B: top=$06, bot=$05  (swapped)
# Mode C: top=$04, bot=$05  (N-1=top, N=bottom, since IDs are odd)
# Mode D: top=$05, bot=$05  (same tile repeated)

print('\nTrying pairing modes for PF3E left slot (tile $05) + right slot (tile $07):')
modes = {
    'A_05top06bot__07top08bot': ((0x05, 0x06), (0x07, 0x08)),
    'B_06top05bot__08top07bot': ((0x06, 0x05), (0x08, 0x07)),
    'C_04top05bot__06top07bot': ((0x04, 0x05), (0x06, 0x07)),
    'D_05top05bot__07top07bot': ((0x05, 0x05), (0x07, 0x07)),
}

for mode_name, (l_pair, r_pair) in modes.items():
    lt, lb = l_pair
    rt, rb = r_pair
    left_16  = tile_to_rgba(get_tile(px, w, lt)) + tile_to_rgba(get_tile(px, w, lb))
    right_16 = tile_to_rgba(get_tile(px, w, rt)) + tile_to_rgba(get_tile(px, w, rb))
    frame = side_by_side(left_16, right_16)
    write_png(str(OUT / f'pf3e_{mode_name}_8x.png'), scale(frame, 8))
    print(f'  pf3e_{mode_name}_8x.png')

# Also try PF3F same modes
print('\nTrying pairing modes for PF3F (tiles $01,$03):')
modes_3f = {
    'A_01top02bot__03top04bot': ((0x01, 0x02), (0x03, 0x04)),
    'B_02top01bot__04top03bot': ((0x02, 0x01), (0x04, 0x03)),
    'C_00top01bot__02top03bot': ((0x00, 0x01), (0x02, 0x03)),
}
for mode_name, (l_pair, r_pair) in modes_3f.items():
    lt, lb = l_pair
    rt, rb = r_pair
    left_16  = tile_to_rgba(get_tile(px, w, lt)) + tile_to_rgba(get_tile(px, w, lb))
    right_16 = tile_to_rgba(get_tile(px, w, rt)) + tile_to_rgba(get_tile(px, w, rb))
    frame = side_by_side(left_16, right_16)
    write_png(str(OUT / f'pf3f_{mode_name}_8x.png'), scale(frame, 8))
    print(f'  pf3f_{mode_name}_8x.png')

print('\nDone. Output in:', OUT)
