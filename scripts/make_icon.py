# -*- coding: utf-8 -*-
"""توليد أيقونة اجوبي PDF (أحجام متعددة داخل ملف ico واحد)"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets = os.path.join(base, "assets")
os.makedirs(assets, exist_ok=True)

S = 512  # نرسم كبيراً ثم ننزل الأحجام


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_gradient(size, c1, c2):
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size - 2)
            px[x, y] = lerp(c1, c2, t)
    return img


# 1) خلفية متدرجة أزرق->تركوازي
grad = make_gradient(S, (28, 74, 153), (16, 165, 158)).convert("RGBA")

# 2) قناع الشكل الدائري الحواف
mask = Image.new("L", (S, S), 0)
mdraw = ImageDraw.Draw(mask)
mdraw.rounded_rectangle([0, 0, S - 1, S - 1], radius=110, fill=255)

icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
icon.paste(grad, (0, 0), mask)

draw = ImageDraw.Draw(icon)

# 3) ظل خفيف للمستند
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(shadow)
sdraw.rounded_rectangle([166, 92, 366, 420], radius=18, fill=(0, 0, 0, 90))
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
icon.alpha_composite(shadow)

# 4) المستند الأبيض بزاوية مطوية
doc_l, doc_t, doc_r, doc_b = 156, 82, 356, 410
draw.rounded_rectangle([doc_l, doc_t, doc_r, doc_b], radius=18, fill=(255, 255, 255, 245))
fold = 52
draw.polygon([(doc_r - fold, doc_t), (doc_r, doc_t + fold), (doc_r - fold, doc_t + fold)],
             fill=(215, 222, 230, 255))
draw.polygon([(doc_r - fold, doc_t), (doc_r, doc_t + fold), (doc_r - fold, doc_t + fold)],
             outline=(160, 170, 185, 255))

# 5) أسطر نص رمادية
for i, w in enumerate([150, 130, 110, 140]):
    y = 170 + i * 42
    draw.rounded_rectangle([doc_l + 28, y, doc_l + 28 + w, y + 14], radius=7,
                           fill=(185, 195, 208, 255))

# 6) شارة حمراء بحرف A
badge_cx, badge_cy, badge_r = 358, 368, 78
draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
              badge_cx + badge_r, badge_cy + badge_r], fill=(227, 62, 48, 255))
draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
              badge_cx + badge_r, badge_cy + badge_r],
             outline=(190, 40, 30, 255), width=4)
try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 88)
except Exception:
    font = ImageFont.load_default(size=88)
bbox = draw.textbbox((0, 0), "A", font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text((badge_cx - tw / 2 - bbox[0], badge_cy - th / 2 - bbox[1]), "A",
          font=font, fill=(255, 255, 255, 255))

# 7) حفظ أحجام متعددة
sizes = [256, 128, 64, 48, 32, 16]
frames = [icon.resize((s, s), Image.LANCZOS) for s in sizes]
ico_path = os.path.join(assets, "ajouby.ico")
frames[0].save(ico_path, format="ICO",
               sizes=[(s, s) for s in sizes],
               append_images=frames[1:])

png_path = os.path.join(assets, "ajouby.png")
icon.resize((256, 256), Image.LANCZOS).save(png_path)

print("ICON SAVED:", ico_path)
print("PNG SAVED:", png_path)
