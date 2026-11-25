# P005 "Two Towns, One Line": the M01-D04 skyline as one band, cold left (Sarah, -12°C), warm right (Sam, 12°C).
# PIL only, no image calls. Output: CH01/P005/assets/img/HERO.jpg (2x of the 792 x BAND_H pt band).
import random, sys
from PIL import Image, ImageFilter, ImageDraw, ImageOps, ImageChops
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
BAND_W, BAND_H = 792, float(sys.argv[1]) if len(sys.argv) > 1 else 180
Y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 20
W, H = BAND_W * 2, int(BAND_H * 2)
src = Image.open(T + "BagroundGenTask/out/plates/M01-D04.png").convert("RGB")
ch = 1024 * BAND_H / BAND_W
im = src.crop((0, Y0, 1024, int(Y0 + ch))).transpose(Image.FLIP_LEFT_RIGHT)   # moon to the cold side
im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2))
def chmul(img, k):
    return Image.merge("RGB", [c.point(lambda v, f=f: min(255, int(v * f))) for c, f in zip(img.split(), k)])
def smooth(lo, hi, v):
    t = min(1, max(0, (v / 255 - lo) / (hi - lo))); return int(255 * t * t * (3 - 2 * t))
random.seed(11)
# warm: lamp gold, a little lift, golden haze pooled low-right
warm = chmul(im, (1.10, 1.01, 0.86))
haze = Image.new("L", (W, H), 0); d = ImageDraw.Draw(haze)
for cx, cy, r in ((W * .78, H * .55, H * .9), (W * .62, H * .35, H * .6), (W * .95, H * .3, H * .7)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=70)
haze = haze.filter(ImageFilter.GaussianBlur(H * .35))
warm = Image.composite(Image.new("RGB", (W, H), (247, 198, 132)), warm, haze)
# cold: desaturate, blue, lifted highlights become ice
gray = ImageOps.grayscale(im)
cold = Image.blend(im, gray.convert("RGB"), 0.6)
cold = chmul(cold, (0.78, 0.93, 1.20))
cold = cold.point(lambda v: int(255 - (255 - v) ** 1.18 / 255 ** 0.18))
ice = Image.new("RGB", (W, H), (222, 238, 255))
cold = Image.composite(ice, cold, gray.point(lambda v: int(120 * min(1, max(0, (v / 255 - .5) / .5)))))
# seam at the centre (0): soft blend over ~ +-60 pt
seam = Image.linear_gradient("L").rotate(90, expand=True).resize((W, H)).point(lambda v: smooth(.42, .58, v))
img = Image.composite(warm, cold, seam)
# frost creeping in from the left edge and along the top-left
fr = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fr)
for i in range(700):
    y = random.uniform(0, H); x = abs(random.gauss(0, 70)); r = random.uniform(2, 9)
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(70, 170))
for i in range(260):
    x = abs(random.gauss(0, 260)); y = abs(random.gauss(0, 26)); r = random.uniform(2, 7)
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(60, 150))
img = Image.composite(Image.new("RGB", (W, H), (234, 243, 255)), img, fr.filter(ImageFilter.GaussianBlur(4)))
# falling snow, cold side only, thinning towards the seam
sn = Image.new("L", (W, H), 0); d = ImageDraw.Draw(sn)
for i in range(900):
    x = random.uniform(0, W * 0.55); y = random.uniform(0, H)
    if random.random() < (x / (W * 0.55)) ** 1.6: continue
    r = random.choice([1.2, 1.6, 2.2, 2.8, 3.6])
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(150, 235))
img = Image.composite(Image.new("RGB", (W, H), (246, 250, 255)), img, sn.filter(ImageFilter.GaussianBlur(.9)))
out = T + "PdfSheetsGenTask/CH01/P005/assets/img/HERO.jpg"
img.save(out, quality=88)
print(out, img.size)
