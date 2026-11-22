from PIL import Image, ImageDraw, ImageFilter
T = "/home/akasdh/Desktop/Projects/ComicAgent/Tasks/"
pg = T + "PdfSheetsGenTask/CH01/P039/assets/img/"
def cut(src, poly, scale=3, feather=2.2, pad=6):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    m = Image.new("L", (W * scale, H * scale), 0)
    ImageDraw.Draw(m).polygon([(x * scale, y * scale) for x, y in poly], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA"); out.putalpha(m)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return out.crop((max(0, min(xs) - pad), max(0, min(ys) - pad), min(W, max(xs) + pad), min(H, max(ys) + pad)))
tez = [(383,186),(410,190),(440,226),(480,244),(520,266),(548,282),(566,298),(595,292),(632,300),(645,324),(650,352),(642,384),(624,398),(604,410),(578,424),(570,450),(554,476),(526,486),(512,500),(518,560),(524,600),(533,667),(540,733),(548,762),(536,785),(482,802),(428,812),(380,818),(322,812),(300,800),(282,790),(255,812),(180,818),(130,794),(116,748),(130,707),(167,673),(213,664),(224,650),(240,612),(272,560),(298,508),(330,462),(324,428),(318,380),(318,334),(328,296),(338,258),(358,214)]
box = [(772,288),(969,318),(950,452),(935,462),(933,535),(843,602),(638,533),(638,460),(752,417)]
t = cut(pg + "V-TEZ-P039.jpg", tez); t.save(pg + "TEZ.png")
b = cut(T + "BagroundGenTask/out/plates/S04-B01.png", box, feather=1.2); b.save(pg + "PACK.png")
chk = Image.new("RGB", (t.width + b.width + 40, max(t.height, b.height) + 20), (190, 60, 60))
chk.paste(t, (10, 10), t); chk.paste(b, (t.width + 30, 10), b); chk.save("cut-check.jpg", quality=85)
print(t.size, b.size)
# scene + glass
W, H = 1728, 1296
im = Image.open(T + "BagroundGenTask/out/plates/S04-B01.png").convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
im.save(pg + "SCENE.jpg", quality=88)
im.resize((864, 648), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10)).save(pg + "GLASS.jpg", quality=85)
