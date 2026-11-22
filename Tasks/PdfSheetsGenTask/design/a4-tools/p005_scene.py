# P005: one street, warm on the right (Sam, 12°C), frozen on the left (Sarah, -12°C). PIL only.
import random
from PIL import Image, ImageFilter, ImageDraw, ImageOps, ImageChops
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
W, H = 1728, 1296
im = Image.open(T + "BagroundGenTask/out/plates/M01-D02.png").convert("RGB").resize((W, H), Image.LANCZOS)
im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
def chmul(img, k):
    return Image.merge("RGB", [c.point(lambda v, f=f: min(255, int(v * f))) for c, f in zip(img.split(), k)])
def smooth(lo, hi, v):
    t = min(1, max(0, (v / 255 - lo) / (hi - lo))); return int(255 * t * t * (3 - 2 * t))
warm = chmul(im, (1.06, 1.0, 0.92))
gray = ImageOps.grayscale(im)
cold = Image.blend(im, gray.convert("RGB"), 0.62)
cold = chmul(cold, (0.76, 0.92, 1.22))
cold = cold.point(lambda v: int(255 - (255 - v) ** 1.22 / 255 ** 0.22))
ice = Image.new("RGB", (W, H), (220, 238, 255))
cold = Image.composite(ice, cold, gray.point(lambda v: int(150 * min(1, max(0, (v / 255 - .5) / .5)))))
# rime on the ground
random.seed(7)
noise = Image.effect_noise((W // 5, H // 5), 70).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))
ground = Image.linear_gradient("L").resize((W, H)).point(lambda v: smooth(.70, 1.0, v))
cold = Image.composite(Image.new("RGB", (W, H), (230, 242, 255)), cold, ImageChops.multiply(ground, noise.point(lambda v: min(255, int(v * 1.1)))))
# seam: cold left, warm right
seam = Image.linear_gradient("L").rotate(90, expand=True).resize((W, H)).point(lambda v: smooth(.40, .60, v))
img = Image.composite(warm, cold, seam)
# frost creeping from the left edge
fr = Image.new("L", (W, H), 0); d = ImageDraw.Draw(fr)
for i in range(1100):
    y = random.uniform(0, H); x = abs(random.gauss(0, 85)); r = random.uniform(2, 10)
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(70, 170))
for i in range(500):   # rime along the bottom-left
    x = abs(random.gauss(0, 520)); y = H - abs(random.gauss(0, 50)); r = random.uniform(2, 8)
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(60, 150))
img = Image.composite(Image.new("RGB", (W, H), (232, 242, 255)), img, fr.filter(ImageFilter.GaussianBlur(5)))
# snow, frozen side only, thinning towards the seam
sn = Image.new("L", (W, H), 0); d = ImageDraw.Draw(sn)
for i in range(1500):
    x = random.uniform(0, W * 0.56); y = random.uniform(0, H)
    if random.random() < (x / (W * 0.56)) ** 1.5: continue
    r = random.choice([1.3, 1.8, 2.4, 3.2, 4.5])
    d.ellipse([x - r, y - r, x + r, y + r], fill=random.randint(150, 240))
img = Image.composite(Image.new("RGB", (W, H), (246, 250, 255)), img, sn.filter(ImageFilter.GaussianBlur(1)))
pg = T + "PdfSheetsGenTask/CH01/P005/assets/img/"
img.save(pg + "SCENE.jpg", quality=88)
img.resize((864, 648), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)).save(pg + "GLASS.jpg", quality=85)
img.resize((1152, 864)).save("p005-scene-preview.jpg", quality=80)
