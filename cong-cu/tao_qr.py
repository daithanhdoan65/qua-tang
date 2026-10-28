"""Tao the QR qua tang: ma QR cham bo tron + logo hop qua, khung hoa van ngau nhien moi lan xuat.

python tao_qr.py --url <dia chi> --chu-de "Về yêu đời" --out <file.png> [--seed N]
"""
import argparse, math, random
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "C:/Windows/Fonts/"
# (nen tren, nen duoi, mau nhan, mau chu, mau hoa van)
BANG_MAU = [
    ((255, 236, 222), (246, 184, 160), (196, 84, 60), (74, 52, 46), [(232, 140, 110), (250, 205, 150), (255, 250, 245)]),
    ((232, 244, 236), (170, 214, 190), (47, 122, 99), (30, 56, 48), [(110, 180, 150), (240, 210, 120), (255, 255, 250)]),
    ((236, 240, 252), (178, 194, 236), (70, 90, 170), (36, 44, 80), [(140, 160, 225), (250, 210, 140), (255, 255, 255)]),
    ((252, 238, 246), (236, 178, 206), (178, 64, 118), (78, 40, 58), [(225, 130, 175), (255, 214, 150), (255, 250, 252)]),
    ((255, 246, 222), (244, 206, 132), (184, 112, 30), (78, 56, 26), [(236, 170, 80), (210, 120, 90), (255, 252, 240)]),
    ((240, 236, 250), (196, 182, 232), (110, 76, 170), (50, 38, 78), [(170, 150, 220), (245, 190, 200), (255, 255, 255)]),
]


def ve_hoa(d, x, y, r, mau, tam):
    for k in range(5):
        a = k * 2 * math.pi / 5
        cx, cy = x + math.cos(a) * r * .55, y + math.sin(a) * r * .55
        d.ellipse([cx - r * .45, cy - r * .45, cx + r * .45, cy + r * .45], fill=mau)
    d.ellipse([x - r * .3, y - r * .3, x + r * .3, y + r * .3], fill=tam)


def ve_sao(d, x, y, r, mau):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * .45
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=mau)


def ve_tim(d, x, y, r, mau):
    d.ellipse([x - r, y - r * .6, x, y + r * .4], fill=mau)
    d.ellipse([x, y - r * .6, x + r, y + r * .4], fill=mau)
    d.polygon([(x - r * .95, y), (x + r * .95, y), (x, y + r * 1.1)], fill=mau)


def ve_la(img, x, y, r, mau, goc):
    l = Image.new("RGBA", (int(r * 4), int(r * 4)), (0, 0, 0, 0))
    ImageDraw.Draw(l).ellipse([r * .6, r * 1.4, r * 3.4, r * 2.6], fill=mau)
    l = l.rotate(goc, resample=Image.BICUBIC)
    img.alpha_composite(l, (max(0, int(x - r * 2)), max(0, int(y - r * 2))))


def hoa_van(img, vung_cam, mau_list, kieu, rng):
    """Rai hoa van trong dai vien, tranh vung_cam (cac hop chu va bang QR)."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    def trung(x, y, r):
        return any(a - r < x < c + r and b - r < y < e + r for a, b, c, e in vung_cam)
    n, tries = 0, 0
    while n < 70 and tries < 4000:
        tries += 1
        r = rng.uniform(10, 26)
        x, y = rng.uniform(50 + r, W - 50 - r), rng.uniform(50 + r, H - 50 - r)
        if trung(x, y, r):
            continue
        m = rng.choice(mau_list[:2])
        if kieu == "hoa":
            ve_hoa(d, x, y, r, m, mau_list[2])
        elif kieu == "sao":
            ve_sao(d, x, y, r, m)
        elif kieu == "tim":
            ve_tim(d, x, y, r * .8, m)
        elif kieu == "la":
            ve_la(img, x, y, r, m, rng.uniform(0, 360))
        else:  # cham bi
            d.ellipse([x - r * .5, y - r * .5, x + r * .5, y + r * .5], fill=m)
        n += 1


def ca_map(size, mau_than, mau_ma):
    """Ca map de thuong ve o 4x roi thu nho cho min."""
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = s / 100
    d.polygon([(14 * u, 52 * u), (2 * u, 32 * u), (6 * u, 56 * u), (2 * u, 76 * u)], fill=mau_than)  # duoi
    d.polygon([(44 * u, 30 * u), (56 * u, 8 * u), (66 * u, 32 * u)], fill=mau_than)  # vay lung
    d.ellipse([10 * u, 26 * u, 96 * u, 82 * u], fill=mau_than)  # than
    d.chord([20 * u, 46 * u, 96 * u, 86 * u], 0, 180, fill=(255, 255, 255))  # bung
    d.polygon([(46 * u, 66 * u), (38 * u, 88 * u), (58 * u, 70 * u)], fill=mau_than)  # vay ngang
    d.ellipse([70 * u, 42 * u, 79 * u, 52 * u], fill=(40, 40, 52))  # mat
    d.ellipse([74 * u, 43 * u, 77 * u, 46 * u], fill=(255, 255, 255))
    d.arc([72 * u, 54 * u, 88 * u, 66 * u], 20, 160, fill=(40, 40, 52), width=int(2.2 * u))  # cuoi
    d.ellipse([62 * u, 54 * u, 70 * u, 60 * u], fill=mau_ma)  # ma hong
    return im.resize((size, size), Image.LANCZOS)


def tao(url, chu_de, out, seed=None):
    rng = random.Random(seed)
    top, bot, nhan, chu, mau_hv = rng.choice(BANG_MAU)
    kieu = rng.choice(["hoa", "sao", "tim", "la", "cham"])

    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=22, border=2)
    q.add_data(url); q.make(fit=True)
    qr = q.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer(),
                      eye_drawer=RoundedModuleDrawer(radius_ratio=1),
                      color_mask=RadialGradiantColorMask(back_color=(255, 255, 255), center_color=nhan, edge_color=chu)).convert("RGB")
    S = qr.size[0]
    L = int(S * .22); logo = Image.new("RGBA", (L, L), (0, 0, 0, 0)); g = ImageDraw.Draw(logo); u = L / 20
    vang = (233, 185, 73)
    g.rounded_rectangle([0, 0, L - 1, L - 1], radius=L // 4, fill=(255, 255, 255), outline=vang, width=max(4, L // 28))
    g.rounded_rectangle([5 * u, 9 * u, 15 * u, 16 * u], radius=u, fill=nhan)
    g.rounded_rectangle([4 * u, 7 * u, 16 * u, 9.6 * u], radius=u, fill=nhan)
    g.rectangle([9.2 * u, 7 * u, 10.8 * u, 16 * u], fill=vang)
    g.ellipse([6 * u, 4 * u, 9.8 * u, 7.4 * u], outline=vang, width=int(1.2 * u))
    g.ellipse([10.2 * u, 4 * u, 14 * u, 7.4 * u], outline=vang, width=int(1.2 * u))
    qr.paste(logo, ((S - L) // 2, (S - L) // 2), logo)

    pad = 40
    W = S + 2 * pad + 220
    y_title, y_sub, y_panel = 70, 165, 240
    P = S + 2 * pad
    y_scan = y_panel + P + 40
    y_sign = y_scan + 80
    sz_shark = 150
    y_shark = y_sign + 64
    H = y_shark + sz_shark + 60

    bg = Image.new("RGB", (W, H))
    bd = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        bd.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    bg = bg.convert("RGBA")

    ft = ImageFont.truetype(FONT + "timesi.ttf", 66)
    fs = ImageFont.truetype(FONT + "timesi.ttf", 42)
    fq = ImageFont.truetype(FONT + "times.ttf", 36)
    fk = ImageFont.truetype(FONT + "timesbi.ttf", 46)
    px = (W - P) // 2
    dd = ImageDraw.Draw(bg)
    def hop(t, y, f):
        w = dd.textlength(t, font=f); return [(W - w) / 2, y, (W + w) / 2, y + f.size * 1.25]
    tit, sub = "Một món quà nhỏ dành cho bạn", chu_de
    cam = [hop(tit, y_title, ft), hop(sub, y_sub, fs), [px, y_panel, px + P, y_panel + P],
           hop("Quét mã bằng camera điện thoại để mở", y_scan, fq), hop("Cá Mập gửi tặng", y_sign, fk),
           [(W - sz_shark) / 2, y_shark, (W + sz_shark) / 2, y_shark + sz_shark]]
    cam = [[a - 14, b - 10, c + 14, e + 10] for a, b, c, e in cam]
    hoa_van(bg, cam, mau_hv, kieu, rng)

    # vien kep bo tron quanh the
    dd = ImageDraw.Draw(bg)
    dd.rounded_rectangle([18, 18, W - 18, H - 18], radius=36, outline=mau_hv[2], width=4)
    dd.rounded_rectangle([30, 30, W - 30, H - 30], radius=28, outline=nhan + (110,), width=2)

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([px, y_panel + 10, px + P, y_panel + P + 10], radius=40, fill=chu + (70,))
    sh = sh.filter(ImageFilter.GaussianBlur(16)); bg.alpha_composite(sh)
    dd = ImageDraw.Draw(bg)
    dd.rounded_rectangle([px, y_panel, px + P, y_panel + P], radius=40, fill=(255, 255, 255))
    bg.paste(qr, (px + pad, y_panel + pad))

    def ctr(t, y, f, col):
        w = dd.textlength(t, font=f); dd.text(((W - w) / 2, y), t, font=f, fill=col)
    ctr(tit, y_title, ft, chu)
    ctr(sub, y_sub, fs, nhan)
    ctr("Quét mã bằng camera điện thoại để mở", y_scan, fq, chu)
    ctr("Cá Mập gửi tặng", y_sign, fk, nhan)
    shark = ca_map(sz_shark, (112, 150, 186), (246, 160, 170))
    bg.alpha_composite(shark, ((W - sz_shark) // 2, y_shark))
    bg.convert("RGB").save(out)
    return kieu


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--chu-de", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    print("hoa van:", tao(a.url, a.chu_de, a.out, a.seed))
