from PIL import Image
img = Image.open('C:/Users/pkordis/Projects/smb3dasm/CHR/chr004.pcx')
vals = set()
for x in range(128):
    for y in range(32):
        vals.add(img.getpixel((x, y)))
print('mode:', img.mode)
print('unique pixel values in chr004:', sorted(vals))

# Show actual pixel values in the coin tile (local 8 and 9)
print('\nTile 8 (top of coin frame_0):')
for y in range(8):
    row = [img.getpixel((8*0 + x, 8*0 + y)) for x in range(8)]
    print(' ', row)
print('\nTile 9 (bottom of coin frame_0):')
for y in range(8):
    row = [img.getpixel((8*1 + x, 8*0 + y)) for x in range(8)]
    print(' ', row)

# Check tile layout - is it 16 cols x 4 rows?
print('\nImage size:', img.size)
print('Tiles per row:', img.width // 8)
print('Tile rows:', img.height // 8)

# Show tiles 0-15 raw values (first row)
for tile_idx in range(16):
    col = tile_idx % 16
    row_t = tile_idx // 16
    vals_in_tile = [img.getpixel((col*8+x, row_t*8+y)) for y in range(8) for x in range(8)]
    nonzero = [v for v in vals_in_tile if v != 0]
    print(f'  tile {tile_idx:2d}: nonzero count={len(nonzero)}, unique={sorted(set(vals_in_tile))}')
