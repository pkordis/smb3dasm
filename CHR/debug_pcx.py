from PIL import Image
import os

chr_dir = r'C:\Users\pkordis\Projects\smb3dasm\CHR'
chr079 = Image.open(os.path.join(chr_dir, 'chr079.pcx'))

print(f"Image mode: {chr079.mode}")
print(f"Image size: {chr079.size}")

# Get unique colors at tile 12 (for coin)
tile_idx = 12
col = tile_idx % 16
row = tile_idx // 16
x0 = col * 8
y0 = row * 8

print(f"\nTile {tile_idx} at ({x0}, {y0}):")
colors = set()
for y in range(8):
    row_str = ""
    for x in range(8):
        pix = chr079.getpixel((x0 + x, y0 + y))
        colors.add(pix)
        row_str += str(pix) + " "
    print(row_str)

print(f"\nUnique colors in tile {tile_idx}: {sorted(colors)}")

# Let's also check the palette if it's a P mode image
if chr079.mode == 'P':
    print("\nPalette mode - getting raw indices:")
    for y in range(8):
        row_str = ""
        for x in range(8):
            # Get raw palette index
            pix = chr079.getpixel((x0 + x, y0 + y))
            row_str += f"{pix} "
        print(row_str)
