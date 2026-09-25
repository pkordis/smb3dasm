from pathlib import Path
import struct

data = Path(r'C:\Users\pkordis\Projects\smb3dasm\CHR\chr083.pcx').read_bytes()
print('PCX header:')
print(f'  manufacturer={data[0]}, version={data[1]}, encoding={data[2]}, bpp={data[3]}')
xmin = struct.unpack_from('<H', data, 4)[0]
ymin = struct.unpack_from('<H', data, 6)[0]
xmax = struct.unpack_from('<H', data, 8)[0]
ymax = struct.unpack_from('<H', data, 10)[0]
print(f'  xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}')
color_planes = data[65]
bytes_per_line = struct.unpack_from('<H', data, 66)[0]
print(f'  color_planes={color_planes}, bytes_per_line={bytes_per_line}')
width = xmax - xmin + 1
height = ymax - ymin + 1
print(f'  image size: {width}x{height}')

print('EGA palette at offset 16:')
for i in range(16):
    r, g, b = data[16 + i*3], data[16 + i*3 + 1], data[16 + i*3 + 2]
    print(f'  [{i}] RGB({r},{g},{b})')

if data[-769] == 0x0C:
    print('VGA 256-color palette at end of file:')
    for i in range(32):
        r, g, b = data[-768 + i*3], data[-768 + i*3 + 1], data[-768 + i*3 + 2]
        print(f'  [{i}] RGB({r},{g},{b})')
else:
    print(f'No VGA palette (marker={data[-769]})')

# Decode RLE
raw = []
i = 128
total = height * bytes_per_line * color_planes
while len(raw) < total + 200 and i < len(data):
    byte = data[i]; i += 1
    if (byte & 0xC0) == 0xC0:
        count = byte & 0x3F
        val = data[i]; i += 1
        raw.extend([val] * count)
    else:
        raw.append(byte)

print(f'Decoded {len(raw)} bytes, expected {total}')
print('Unique pixel values:', sorted(set(raw[:total])))

print('First 8 rows of decoded pixels (raw):')
for row in range(8):
    line = raw[row * bytes_per_line : row * bytes_per_line + 32]
    print(f'  row {row}: {line}')

# Show tile area where tiles $00-$08 live
# tiles_per_row = 128/8 = 16
# tile $00 = col 0, row 0 -> px (0,0)
# tile $01 = col 1, row 0 -> px (8,0)
# tile $05 = col 5, row 0 -> px (40,0)
print('\nTile $01 pixels (8x16 mode: tiles $01 top half, $02 bottom half):')
for row in range(16):
    if row < 8:
        tile_col, tile_row = 1, 0
        py = tile_row * 8 + row
    else:
        tile_col, tile_row = 2, 0
        py = tile_row * 8 + (row - 8)
    px = tile_col * 8
    line = raw[py * bytes_per_line + px : py * bytes_per_line + px + 8]
    print(f'  row {row}: {line}')

print('\nTile $05 pixels (8x16 mode: tiles $05 top half, $06 bottom half):')
for row in range(16):
    if row < 8:
        tile_col, tile_row = 5, 0
        py = tile_row * 8 + row
    else:
        tile_col, tile_row = 6, 0
        py = tile_row * 8 + (row - 8)
    px = tile_col * 8
    line = raw[py * bytes_per_line + px : py * bytes_per_line + px + 8]
    print(f'  row {row}: {line}')
