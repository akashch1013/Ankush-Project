# P039 scene: S04-B01 with the painted stock labels blanked (no stray numbers), mirrored so the big open box sits
# under the reading panes and the marble counter at the right is free for the nine packs.
from PIL import Image, ImageFilter, ImageDraw, ImageStat
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
pg = T + "PdfSheetsGenTask/CH01/P039/assets/img/"
im = Image.open(T + "BagroundGenTask/out/plates/S04-B01.png").convert("RGB")
for box in ((246, 272, 392, 340), (524, 302, 698, 383)):
    reg = im.crop(box)
    px = sorted(reg.getdata(), key=lambda p: -sum(p))[: len(reg.getdata()) // 3]
    avg = tuple(sum(c[i] for c in px) // len(px) for i in range(3))
    flat = Image.new("RGB", reg.size, avg)
    shade = reg.filter(ImageFilter.GaussianBlur(18))
    fill = Image.blend(shade, flat, 0.55)
    m = Image.new("L", reg.size, 0); ImageDraw.Draw(m).rounded_rectangle((4, 4, reg.size[0] - 5, reg.size[1] - 5), 6, fill=255)
    im.paste(fill, box[:2], m.filter(ImageFilter.GaussianBlur(2.5)))
im = im.transpose(Image.FLIP_LEFT_RIGHT)
im.crop((300, 230, 800, 420)).save("labels-check.jpg", quality=85)
W, H = 1728, 1296
big = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
big.save(pg + "SCENE.jpg", quality=88)
big.resize((864, 648), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)).save(pg + "GLASS.jpg", quality=85)
