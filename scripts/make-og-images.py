#!/usr/bin/env python3
"""Renders one 1200x627 share image per tool into assets/og/ (LinkedIn's size).

Needs Pillow and the brand fonts (Google Fonts, OFL), which are not kept in this repo:
  Montserrat[wght].ttf, Poppins-Medium.ttf, Poppins-SemiBold.ttf
Usage: python3 scripts/make-og-images.py --fonts /path/to/font/folder
Colors are the brand palette only; gold is a decorative bar, never text.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 627
NAVY, NAVY_DARK, GOLD, LIGHT = "#044771", "#033359", "#F1BE5C", "#F4F6F8"

TOOLS = [
    ("scorecard", "Owner-Dependency Scorecard", "See how much your business still runs on you. 10\u00a0questions, 2\u00a0minutes."),
    ("calculator", "Cost of Owner Dependence Calculator", "Turn your admin hours and dropped leads into a yearly dollar cost."),
    ("ai-readiness", "AI Employee Readiness Assessment", "Find the one AI assistant to start with, and whether you're ready for it."),
    ("foundation-score", "Foundation Readiness Score", "Check your legal, money, brand, offer and sales basics before you grow."),
    ("system-finder", "Business System Finder", "Find out which build your business needs next. 7\u00a0questions, 2\u00a0minutes."),
    ("guides", "The Run-Without-You Guide", "A free 25-point checklist, plus a 90-day\u00a0plan to fix the\u00a0gaps."),
]


def lum(hex_color):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split(" "):  # split on plain spaces only, so \u00a0 keeps "7 questions" together
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= width or not line:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def fit(draw, text, make_font, sizes, width, max_lines):
    for size in sizes:
        font = make_font(size)
        lines = wrap(draw, text, font, width)
        if len(lines) <= max_lines and all(draw.textlength(l, font=font) <= width for l in lines):
            return font, lines, size
    sys.exit("text does not fit: " + text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True, help="folder with Montserrat[wght].ttf, Poppins-Medium.ttf, Poppins-SemiBold.ttf")
    fonts = pathlib.Path(ap.parse_args().fonts)

    def montserrat(size):
        f = ImageFont.truetype(str(fonts / "Montserrat[wght].ttf"), size)
        f.set_variation_by_axes([800])
        return f

    def poppins(name):
        return lambda size: ImageFont.truetype(str(fonts / name), size)

    for fg, bg in ((LIGHT, NAVY), (LIGHT, NAVY_DARK)):
        ratio = contrast(fg, bg)
        assert ratio >= 7, (fg, bg, ratio)
        print("contrast %s on %s = %.1f:1" % (fg, bg, ratio))

    out = ROOT / "assets" / "og"
    out.mkdir(parents=True, exist_ok=True)
    left, text_w, band_h = 84, 1032, 112
    for slug, name, promise in TOOLS:
        img = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(img)
        d.rectangle([0, H - band_h, W, H], fill=NAVY_DARK)
        d.rounded_rectangle([left, 92, left + 96, 100], radius=4, fill=GOLD)  # decorative bar

        tfont, tlines, tsize = fit(d, name, montserrat, range(78, 47, -2), text_w, 2)
        pfont, plines, psize = fit(d, promise, poppins("Poppins-Medium.ttf"), range(38, 27, -1), text_w, 2)
        t_lh, p_lh = int(tsize * 1.16), int(psize * 1.45)
        block = len(tlines) * t_lh + 34 + len(plines) * p_lh
        y = 128 + ((H - band_h - 128 - 36) - block) // 2
        for line in tlines:
            d.text((left, y), line, font=tfont, fill=LIGHT)
            y += t_lh
        y += 34
        for line in plines:
            d.text((left, y), line, font=pfont, fill=LIGHT)
            y += p_lh

        ffont = poppins("Poppins-SemiBold.ttf")(30)
        footer = "Business Plans Plus · Tampa"
        fy = H - band_h + (band_h - 30) // 2 - 6
        d.text((left, fy), footer, font=ffont, fill=LIGHT)
        path = out / (slug + ".png")
        img.save(path, optimize=True)
        print("%s  title %dpx x%d lines, promise %dpx x%d lines" % (path.relative_to(ROOT), tsize, len(tlines), psize, len(plines)))


if __name__ == "__main__":
    main()
