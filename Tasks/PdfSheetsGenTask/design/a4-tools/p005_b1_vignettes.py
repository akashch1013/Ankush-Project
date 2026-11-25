# P005 (B1 light rebuild): two feathered vignettes from M01-D01 (upper-right pavilions):
# TOWNW.png lamp-warm (Sam), TOWNC.png frost-graded with snow (Sarah). Free, PIL only.
import random
from PIL import Image, ImageFilter, ImageDraw, ImageOps, ImageChops
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
OUT = T + "PdfSheetsGenTask/CH01/P005/assets/img/"
W, H = 260, 640                       # 4 px/pt for a 65 x 160 pt slot
src = Image.open(T + "BagroundGenTask/out/plates/M01-D01.png").convert("RGB")
crop = src.crop((786, 96, 912, 406)).resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 50, 2))
CREAM = (247, 241, 227)

def chmul(img, k):
    return Image.merge("RGB", [c.point(lambda v, f=f: min(255, int(v * f))) for c, f in zip(img.split(), k)])

def warm(im):
    w = chmul(im, (1.16, 1.02, 0.78))
    lum = ImageOps.grayscale(im)
    amber = ImageOps.colorize(lum, (70, 38, 22), (255, 226, 170))      # lamp-lit dusk: blue night pulled to amber
    return Image.blend(w, amber, 0.62)

def cold(im, seed):
    random.seed(seed)
    gray = ImageOps.grayscale(im)
    c = Image.blend(im, gray.convert("RGB"), 0.62)
    c = chmul(c, (0.78, 0.92, 1.20))
    c = c.point(lambda v: int(255 - (255 - v) ** 1.22 / 255 ** 0.22))
    ice = Image.new("RGB", im.size, (220, 238, 255))
    c = Image.composite(ice, c, gray.point(lambda v: int(150 * min(1, max(0, (v / 255 - .5) / .5)))))
    sn = Image.new("L", im.size, 0); d = ImageDraw.Draw(sn)
    for _ in range(170):
        x = random.uniform(0, W); y = random.uniform(0, H); r = random.choice([1.2, 1.6, 2.2, 3.0])
        d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(150, 240))
    # rime settling on the lower third
    for _ in range(120):
        x = random.uniform(0, W); y = H - abs(random.gauss(0, 70)); r = random.uniform(2, 6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(70, 150))
    return Image.composite(Image.new("RGB", im.size, (244, 249, 255)), c, sn.filter(ImageFilter.GaussianBlur(1)))

def feather(seed, rough=True):
    """irregular fade: an inset rounded field roughed up by noise, edges dissolving into the paper"""
    random.seed(seed)
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle([34, 46, W - 30, H - 52], radius=40, fill=255)
    for _ in range(90):   # ragged bites and spurs along the edge
        side = random.choice("lrtb")
        if side in "lr":
            y = random.uniform(40, H - 40); x = 34 if side == "l" else W - 30
        else:
            x = random.uniform(30, W - 30); y = 46 if side == "t" else H - 52
        r = random.uniform(8, 26)
        d.ellipse([x - r, y - r, x + r, y + r], fill=random.choice([0, 255]))
    m = m.filter(ImageFilter.GaussianBlur(16))
    # roughen only the fading rim (0 < alpha < 255), never the interior
    n = Image.effect_noise((W // 5, H // 5), 70).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))
    rim = m.point(lambda v: 255 if 8 < v < 235 else 0).filter(ImageFilter.GaussianBlur(6))
    rough_m = ImageChops.multiply(m, n.point(lambda v: min(255, 90 + v)))
    if rough:
        m = Image.composite(rough_m, m, rim)
    return m.point(lambda v: min(255, int(v * 1.12)))

for name, img, seed, rough, fade in (("TOWNW", warm(crop), 3, False, .34), ("TOWNC", cold(crop, 11), 5, True, .38)):
    img = Image.blend(img, Image.new("RGB", (W, H), CREAM), fade)    # held under the ticks: low contrast
    out = img.convert("RGBA"); out.putalpha(feather(seed, rough))
    out.save(OUT + name + ".png")
print("ok")

# Ahana: the pillar's outer (left) side dissolves irregularly into the paper (V09 §6), figure stays opaque
a = Image.open(T + "FInalChangesTask/library/C-AHANA-LEAN-01.png").convert("RGBA")
a.thumbnail((886, 1000), Image.LANCZOS)
aw, ah = a.size
random.seed(21)
ramp = Image.new("L", (aw, ah), 255); d = ImageDraw.Draw(ramp)
for y in range(0, ah, 3):                      # ragged fade front, wandering with height
    edge = 70 + 60 * random.random() + 40 * ((y / ah) ** 2)
    for x in range(0, int(edge) + 60, 3):
        v = max(0, min(255, int(255 * (x - edge + 60) / 120)))
        d.rectangle([x, y, x + 3, y + 3], fill=v)
    d.rectangle([int(edge) + 60, y, aw, y + 3], fill=255)
ramp = ramp.filter(ImageFilter.GaussianBlur(7))
n = Image.effect_noise((aw // 14, ah // 14), 80).resize((aw, ah), Image.BICUBIC).filter(ImageFilter.GaussianBlur(4))
ramp = Image.composite(ImageChops.multiply(ramp, n.point(lambda v: min(255, 110 + v))), ramp,
                       ramp.point(lambda v: 255 if 10 < v < 240 else 0).filter(ImageFilter.GaussianBlur(8)))
a.putalpha(ImageChops.multiply(a.split()[3], ramp))
a.save(OUT + "AHANA.png")
print("ahana ok")
