#!/usr/bin/env python3
"""Generate the Natobee logo proposals described in SPEC.md."""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
OUT_DIR = ROOT / "out"

NAVY_A = "#123A55"
NAVY_B = "#0B2E3D"
A_STOPS = (("0%", "#63E0E6"), ("52%", "#24A6DA"), ("100%", "#1667C4"))
B_STOPS = (("0%", "#5FD8EC"), ("50%", "#1595C4"), ("100%", "#0B5E73"))


def fmt(value: float) -> str:
    """Short, stable SVG number formatting."""
    if abs(value) < 0.0000005:
        value = 0.0
    return f"{value:.3f}".rstrip("0").rstrip(".")


def rounded_polygon(points: list[tuple[float, float]], r: float) -> str:
    """Return a closed rounded polygon, inset by r along both incident edges."""
    corners: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for i, point in enumerate(points):
        previous = points[i - 1]
        following = points[(i + 1) % len(points)]

        def toward(target: tuple[float, float]) -> tuple[float, float]:
            dx, dy = target[0] - point[0], target[1] - point[1]
            length = math.hypot(dx, dy)
            distance = min(r, length / 2)
            return point[0] + dx * distance / length, point[1] + dy * distance / length

        corners.append((toward(previous), toward(following)))

    commands = [f"M {fmt(corners[0][1][0])} {fmt(corners[0][1][1])}"]
    for i in range(1, len(points) + 1):
        index = i % len(points)
        before, after = corners[index]
        vertex = points[index]
        commands.append(f"L {fmt(before[0])} {fmt(before[1])}")
        commands.append(
            f"Q {fmt(vertex[0])} {fmt(vertex[1])} {fmt(after[0])} {fmt(after[1])}"
        )
    commands.append("Z")
    return " ".join(commands)


def gradient(gradient_id: str, stops, horizontal: bool = False) -> str:
    x2, y2 = ("1", "0") if horizontal else ("1", "1")
    stop_tags = "".join(
        f'<stop offset="{offset}" stop-color="{colour}"/>' for offset, colour in stops
    )
    return (
        f'<linearGradient id="{gradient_id}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
        f"{stop_tags}</linearGradient>"
    )


A_TRIANGLE = [(47, 34), (47, 86), (89, 60)]
B_HEXAGON = [(32, 9), (88, 9), (116, 60), (88, 111), (32, 111), (4, 60)]
B_TRIANGLE = [(45, 34), (45, 86), (90, 60)]


def icon_a(gradient_id: str) -> str:
    return (
        f'<rect x="4" y="4" width="112" height="112" rx="32" ry="32" '
        f'fill="url(#{gradient_id})"/>'
        f'<path d="{rounded_polygon(A_TRIANGLE, 9)}" fill="#FFFFFF"/>'
    )


def scale_about_center(points, factor: float):
    return [(60 + (x - 60) * factor, 60 + (y - 60) * factor) for x, y in points]


def icon_b(gradient_id: str) -> str:
    return (
        f'<path d="{rounded_polygon(B_HEXAGON, 8)}" fill="url(#{gradient_id})"/>'
        f'<path d="{rounded_polygon(B_TRIANGLE, 3)}" fill="#FFFFFF"/>'
    )


class Wordmark:
    def __init__(self, font_name: str, text: str, spacing_em: float):
        self.font = TTFont(FONT_DIR / font_name)
        self.glyph_set = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.metrics = self.font["hmtx"].metrics
        self.upm = self.font["head"].unitsPerEm
        os2 = self.font["OS/2"]
        self.cap_height = getattr(os2, "sCapHeight", 0) or self.upm * 0.7
        self.x_height = getattr(os2, "sxHeight", 0) or self.cap_height * 0.72
        self.text = text
        self.spacing_em = spacing_em

    def outline(self, x: float, baseline: float, cap_pixels: float):
        scale = cap_pixels / self.cap_height
        pen = SVGPathPen(self.glyph_set)
        cursor = 0.0
        bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]
        for index, char in enumerate(self.text):
            glyph_name = self.cmap[ord(char)]
            glyph = self.glyph_set[glyph_name]
            transform = (scale, 0, 0, -scale, x + cursor * scale, baseline)
            glyph.draw(TransformPen(pen, transform))
            bounds_pen = BoundsPen(self.glyph_set)
            glyph.draw(bounds_pen)
            if bounds_pen.bounds:
                gx0, gy0, gx1, gy1 = bounds_pen.bounds
                bounds[0] = min(bounds[0], x + (cursor + gx0) * scale)
                bounds[1] = min(bounds[1], baseline - gy1 * scale)
                bounds[2] = max(bounds[2], x + (cursor + gx1) * scale)
                bounds[3] = max(bounds[3], baseline - gy0 * scale)
            cursor += self.metrics[glyph_name][0]
            if index < len(self.text) - 1:
                cursor += self.spacing_em * self.upm
        return pen.getCommands(), cursor * scale, tuple(bounds)

    def x_height_pixels(self, cap_pixels: float) -> float:
        return self.x_height * cap_pixels / self.cap_height

    def advance_to(self, character_count: int, cap_pixels: float) -> float:
        """Horizontal position immediately before a character, in output pixels."""
        units = 0.0
        for index, char in enumerate(self.text[:character_count]):
            units += self.metrics[self.cmap[ord(char)]][0]
            if index < character_count - 1:
                units += self.spacing_em * self.upm
        return units * cap_pixels / self.cap_height


def svg_document(width: float, height: float, defs: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(width)} {fmt(height)}" '
        f'width="{fmt(width)}" height="{fmt(height)}" role="img">\n'
        f"  <defs>{defs}</defs>\n  {body}\n</svg>\n"
    )


def write_icon(filename: str, kind: str) -> None:
    gid = filename.removesuffix(".svg").replace("-", "_") + "_gradient"
    stops = A_STOPS if kind == "a" else B_STOPS
    body = icon_a(gid) if kind == "a" else icon_b(gid)
    (OUT_DIR / filename).write_text(svg_document(120, 120, gradient(gid, stops), body), encoding="utf-8")


def write_lockup(filename: str, kind: str, word: Wordmark, *, white=False, accent=False) -> None:
    icon_height = 100.0
    ratio = 1.55 if kind == "a" else 1.7
    cap = icon_height / ratio
    baseline = icon_height / 2 + word.x_height_pixels(cap) / 2
    gap = icon_height * 0.30
    word_x = icon_height + gap
    path, word_width, _ = word.outline(word_x, baseline, cap)
    width = word_x + word_width
    gid = filename.removesuffix(".svg").replace("-", "_") + "_icon_gradient"
    stops = A_STOPS if kind == "a" else B_STOPS
    icon = icon_a(gid) if kind == "a" else icon_b(gid)
    fill = "#FFFFFF" if white else (f"url(#{gid}_word)" if accent else (NAVY_A if kind == "a" else NAVY_B))
    defs = gradient(gid, stops)
    if accent and not white:
        # A single path keeps the wordmark portable. Duplicate stops make a hard
        # colour boundary immediately before the final "ee"; only that suffix
        # traverses the three-colour horizontal gradient.
        suffix_start = word.advance_to(len(word.text) - 2, cap)
        boundary = 100 * suffix_start / word_width
        middle = boundary + (100 - boundary) * 0.52
        defs += (
            f'<linearGradient id="{gid}_word" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{NAVY_A}"/>'
            f'<stop offset="{fmt(boundary)}%" stop-color="{NAVY_A}"/>'
            f'<stop offset="{fmt(boundary)}%" stop-color="#63E0E6"/>'
            f'<stop offset="{fmt(middle)}%" stop-color="#24A6DA"/>'
            '<stop offset="100%" stop-color="#1667C4"/>'
            '</linearGradient>'
        )
    body = (
        f'<g transform="scale({fmt(icon_height / 120)})">{icon}</g>'
        f'<path d="{path}" fill="{fill}"/>'
    )
    (OUT_DIR / filename).write_text(svg_document(width, icon_height, defs, body), encoding="utf-8")


def write_stack(filename: str, kind: str, word: Wordmark, *, white=False) -> None:
    icon_height = 100.0
    ratio = 1.55 if kind == "a" else 1.7
    cap = icon_height / ratio
    gap = icon_height * 0.22
    baseline = icon_height + gap + cap
    _, word_width, _ = word.outline(0, baseline, cap)
    width = max(icon_height, word_width)
    icon_x = (width - icon_height) / 2
    word_x = (width - word_width) / 2
    path, _, bounds = word.outline(word_x, baseline, cap)
    height = max(baseline, bounds[3]) + 3
    gid = filename.removesuffix(".svg").replace("-", "_") + "_gradient"
    stops = A_STOPS if kind == "a" else B_STOPS
    icon = icon_a(gid) if kind == "a" else icon_b(gid)
    fill = "#FFFFFF" if white else (NAVY_A if kind == "a" else NAVY_B)
    body = (
        f'<g transform="translate({fmt(icon_x)} 0) scale({fmt(icon_height / 120)})">{icon}</g>'
        f'<path d="{path}" fill="{fill}"/>'
    )
    (OUT_DIR / filename).write_text(svg_document(width, height, gradient(gid, stops), body), encoding="utf-8")


def image(filename: str, css_class: str = "") -> str:
    return f'<img class="{css_class}" src="{escape(filename)}" alt="">'


def write_sheet() -> None:
    def sns_sizes(filename: str) -> str:
        return "".join(
            f'<div class="size"><img class="sns-icon" src="{filename}" width="{size}" height="{size}" alt="">{size}px</div>'
            for size in (96, 48)
        )

    html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080">
<title>株式会社ナトビー ロゴ案</title>
<style>
@font-face {{ font-family: 'Noto JP'; src: url('../fonts/NotoSansJP-Medium.ttf') format('truetype'); font-weight: 500; font-display: swap; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 1080px; background: #fff; color: {NAVY_B}; font-family: 'Noto JP', sans-serif; }}
.sheet {{ width: 1080px; background: #fff; overflow: hidden; }}
header {{ padding: 42px 60px 30px; border-bottom: 1px solid #dbe7ea; }}
h1 {{ margin: 0 0 8px; font-size: 34px; letter-spacing: .03em; }}
header p {{ margin: 0; color: #52717d; font-size: 17px; }}
section {{ padding: 32px 60px 36px; }}
section + section {{ border-top: 1px solid #dbe7ea; }}
h2 {{ margin: 0 0 24px; font-size: 28px; line-height: 1.35; }}
.current {{ padding-bottom: 32px; }}
.current-box {{ height: 150px; display: flex; align-items: center; gap: 42px; }}
.current-box img {{ display: block; width: 280px; max-height: 120px; object-fit: contain; object-position: left center; }}
.current-box .label {{ margin: 0; }}
.proposal-grid {{ display: grid; grid-template-columns: 320px 1fr; gap: 22px; }}
.card {{ min-width: 0; height: 250px; border: 1px solid #dbe7ea; border-radius: 16px; padding: 20px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #fff; }}
.card img {{ display: block; max-width: 100%; max-height: 180px; }}
.card .big-icon {{ width: 200px; height: 200px; max-height: 200px; }}
.card .lockup {{ width: 100%; min-width: 440px; max-height: 115px; }}
.card .stack {{ height: 180px; max-height: 180px; }}
.label {{ margin-top: 14px; color: #5b7680; font-size: 15px; line-height: 1.4; }}
.dark {{ padding: 30px 60px; min-height: 150px; background: {NAVY_B}; display: flex; align-items: center; gap: 44px; color: #fff; }}
.dark span {{ width: 170px; flex: none; font-size: 15px; opacity: .8; }}
.dark img {{ width: 560px; max-height: 105px; }}
.preview {{ background: #f5f9fa; }}
.preview-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
.preview-group {{ display: flex; align-items: center; gap: 24px; padding: 22px 26px; background: #fff; border-radius: 14px; border: 1px solid #dbe7ea; }}
.preview-group strong {{ width: 24px; flex: none; font-size: 18px; }}
.sizes {{ display: flex; align-items: flex-end; gap: 24px; }}
.size {{ text-align: center; color: #67808a; font-size: 14px; }}
.size img {{ display: block; margin: 0 auto 8px; }}
.sns-icon {{ display: block; object-fit: cover; border-radius: 50%; }}
.names {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
.name-card {{ min-width: 0; height: 180px; padding: 22px; border: 1px solid #dbe7ea; border-radius: 14px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.name-card.wide {{ grid-column: 1 / -1; }}
.word-crop {{ position: relative; width: 380px; height: 112px; overflow: hidden; }}
.word-crop img {{ position: absolute; top: 50%; max-width: none; transform: translateY(-50%); }}
.word-a img {{ width: 508px; left: -128px; }}
.word-b img {{ width: 526.2px; left: -146.4px; }}
.word-caps img {{ width: 480.8px; left: -100.8px; }}
.colours {{ display: grid; grid-template-columns: 1fr 1fr; gap: 44px; }}
.colour-title {{ margin-bottom: 12px; font-size: 16px; }}
.bar {{ height: 54px; border-radius: 12px; }}
.bar-a {{ background: linear-gradient(90deg, #63E0E6 0%, #24A6DA 52%, #1667C4 100%); }}
.bar-b {{ background: linear-gradient(90deg, #5FD8EC 0%, #1595C4 50%, #0B5E73 100%); }}
.hexes {{ margin-top: 10px; color: #58747f; font: 14px/1.5 ui-monospace, monospace; letter-spacing: .02em; }}
</style>
</head>
<body><main class="sheet">
<header><h1>株式会社ナトビー ロゴ案</h1><p>YouTubeらしさは残しつつ、色と形で別物に</p></header>
<section class="current"><h2>今のロゴ</h2><div class="current-box">
<img src="../../deploy-prod/img/logo.svg" width="280" alt="現在のナトビーのロゴ"><div class="label">今のロゴ（赤）</div>
</div></section>
<section><h2>Aパターン｜かわいい系</h2><div class="proposal-grid">
<div class="card">{image('logo-a-icon.svg', 'big-icon')}<div class="label">シンボル</div></div>
<div class="card">{image('logo-a-lockup.svg', 'lockup')}<div class="label">基本の組み合わせ</div></div>
<div class="card">{image('logo-a-stack.svg', 'stack')}<div class="label">縦の組み合わせ</div></div>
<div class="card">{image('logo-a-lockup-accent.svg', 'lockup')}<div class="label">最後の2文字に彩り</div></div>
</div></section>
<div class="dark"><span>濃い背景での表示</span>{image('logo-a-lockup-white.svg')}</div>
<section><h2>Bパターン｜かっこいい系</h2><div class="proposal-grid">
<div class="card">{image('logo-b-icon.svg', 'big-icon')}<div class="label">シンボル</div></div>
<div class="card">{image('logo-b-lockup.svg', 'lockup')}<div class="label">読みやすい表記</div></div>
<div class="card">{image('logo-b-stack.svg', 'stack')}<div class="label">縦の組み合わせ</div></div>
<div class="card">{image('logo-b-lockup-caps.svg', 'lockup')}<div class="label">力強い表記</div></div>
</div></section>
<div class="dark"><span>濃い背景での表示</span>{image('logo-b-lockup-white.svg')}</div>
<section class="preview"><h2>SNSのアイコンにした時</h2><div class="preview-row">
<div class="preview-group"><strong>A</strong><div class="sizes">{sns_sizes('logo-a-icon.svg')}</div></div>
<div class="preview-group"><strong>B</strong><div class="sizes">{sns_sizes('logo-b-icon.svg')}</div></div>
</div></section>
<section class="preview"><h2>小さくした時の見え方</h2><div class="preview-row">
<div class="preview-group"><strong>A</strong><div class="sizes">{small_sizes('logo-a-icon.svg')}</div></div>
<div class="preview-group"><strong>B</strong><div class="sizes">{small_sizes('logo-b-icon.svg')}</div></div>
</div></section>
<section><h2>名前だけで使う時</h2><div class="names">
<div class="name-card wide"><div class="word-crop word-a">{image('logo-a-lockup.svg')}</div><div class="label">A｜natobee</div></div>
<div class="name-card"><div class="word-crop word-b">{image('logo-b-lockup.svg')}</div><div class="label">B｜Natobee</div></div>
<div class="name-card"><div class="word-crop word-caps">{image('logo-b-lockup-caps.svg')}</div><div class="label">B｜NATOBEE</div></div>
</div></section>
<section><h2>使用カラー</h2><div class="colours">
<div><div class="colour-title">Aパターン</div><div class="bar bar-a"></div><div class="hexes">#63E0E6　#24A6DA　#1667C4<br>#123A55</div></div>
<div><div class="colour-title">Bパターン</div><div class="bar bar-b"></div><div class="hexes">#5FD8EC　#1595C4　#0B5E73<br>#0B2E3D</div></div>
</div></section>
</main></body></html>
"""
    (OUT_DIR / "sheet.html").write_text(html, encoding="utf-8")


def small_sizes(filename: str) -> str:
    return "".join(
        f'<div class="size"><img src="{filename}" width="{size}" height="{size}" alt="">{size}px</div>'
        for size in (64, 32, 16)
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a = Wordmark("Quicksand-Bold.ttf", "natobee", 0.02)
    b = Wordmark("Outfit-SemiBold.ttf", "Natobee", 0.015)
    b_caps = Wordmark("Outfit-Medium.ttf", "NATOBEE", 0.20)

    write_icon("logo-a-icon.svg", "a")
    write_lockup("logo-a-lockup.svg", "a", a)
    write_lockup("logo-a-lockup-accent.svg", "a", a, accent=True)
    write_stack("logo-a-stack.svg", "a", a)
    write_icon("logo-b-icon.svg", "b")
    write_lockup("logo-b-lockup.svg", "b", b)
    write_lockup("logo-b-lockup-caps.svg", "b", b_caps)
    write_stack("logo-b-stack.svg", "b", b)

    write_lockup("logo-a-lockup-white.svg", "a", a, white=True)
    write_lockup("logo-a-lockup-accent-white.svg", "a", a, white=True)
    write_stack("logo-a-stack-white.svg", "a", a, white=True)
    write_lockup("logo-b-lockup-white.svg", "b", b, white=True)
    write_lockup("logo-b-lockup-caps-white.svg", "b", b_caps, white=True)
    write_stack("logo-b-stack-white.svg", "b", b, white=True)
    write_sheet()


if __name__ == "__main__":
    main()
