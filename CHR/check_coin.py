from PIL import Image

img = Image.open(r'C:/Users/pkordis/Projects/super-mario-bros-3/src/main/resources/sprites/object/coin/frame_0.png')
colors = set()
for x in range(8):
    for y in range(16):
        colors.add(img.getpixel((x, y)))
print("Colors used:")
for c in sorted(colors):
    print(f"  {c}")

print("\nASCII representation:")
MAP = {
    (0, 0, 0, 0): '.',       # Transparent
    (0, 0, 0, 255): '#',     # Black
    (252, 160, 68, 255): 'o', # Orange
    (252, 252, 252, 255): '@' # White
}
for y in range(16):
    row = ''
    for x in range(8):
        c = img.getpixel((x, y))
        row += MAP.get(c, '?')
    print(row)
