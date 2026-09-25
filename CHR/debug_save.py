import os
from PIL import Image

CHR_DIR = r'C:\Users\pkordis\Projects\smb3dasm\CHR'
PROJECT_ROOT = os.path.join(CHR_DIR, '..', 'super-mario-bros-3')
COIN_DIR = os.path.join(PROJECT_ROOT, 'src', 'main', 'resources', 'sprites', 'object', 'coin')
print('Resolved coin dir:', os.path.abspath(COIN_DIR))

# Read tile correctly
img = Image.open(os.path.join(CHR_DIR, 'chr004.pcx'))

def get_tile(idx):
    col = idx % 16
    row = idx // 16
    return [[img.getpixel((col*8+x, row*8+y)) for x in range(8)] for y in range(8)]

# Show tile 8 (top of coin frame 0)
print('\nTile 8 (local, pattern 0x48):')
for row in get_tile(8):
    print(' ', row)

print('\nTile 9 (local, pattern 0x49):')
for row in get_tile(9):
    print(' ', row)

# Confirm the correct coin frame_0 save
COIN_PAL = {
    0: (0, 0, 0, 0),
    1: (0, 0, 0, 255),
    2: (252, 160, 68, 255),
    3: (252, 252, 252, 255),
}

t8 = get_tile(8)
t9 = get_tile(9)
rows = t8 + t9  # 16 rows total

out = Image.new('RGBA', (8, 16))
for y, row in enumerate(rows):
    for x, idx in enumerate(row):
        out.putpixel((x, y), COIN_PAL[idx])

print('\nframe_0 image size:', out.size)
print('Non-transparent pixels:', sum(1 for x in range(8) for y in range(16) if out.getpixel((x,y))[3] > 0))

dst = os.path.join(COIN_DIR, 'frame_0.png')
os.makedirs(COIN_DIR, exist_ok=True)
out.save(dst)
print('Saved to:', dst)

# Verify it
check = Image.open(dst)
print('Read back size:', check.size)
print('Read back non-transparent:', sum(1 for x in range(8) for y in range(16) if check.getpixel((x,y))[3] > 0))
