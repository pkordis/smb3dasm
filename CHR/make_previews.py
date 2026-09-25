from PIL import Image
import os

BASE = r'C:\Users\pkordis\Projects\super-mario-bros-3\src\main\resources\sprites\object'
OUT  = r'C:\Users\pkordis\Projects\smb3dasm\CHR'
scale = 12

files = [
    'coin/frame_0.png',
    'coin/frame_1.png',
    'coin/frame_2.png',
    'coin/frame_3_hflip.png',
    'score/score_100.png',
    'score/score_1up.png',
    'score/tile_5B.png',
    'score/tile_69.png',
]
for fname in files:
    img = Image.open(os.path.join(BASE, fname))
    out = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    dst = os.path.join(OUT, 'verify_' + fname.replace('/', '_'))
    out.save(dst)
    print(fname, img.size, '->', out.size)
