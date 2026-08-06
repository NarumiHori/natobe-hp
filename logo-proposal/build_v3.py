#!/usr/bin/env python3
"""Generate the final Natobe v3 logo in the two proposed colourways."""

from __future__ import annotations

import base64
from pathlib import Path

from build import Wordmark, fmt, gradient, svg_document
from build_v2 import icon_v2


# PM-adjustable final play-mark settings.
FINAL_TRI_DX = -3.75
FINAL_TRI_SCALE = 1.06
ICON_TO_CAP = 1.72
ICON_GAP = 0.20

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out" / "v3"
FONT_FILE = ROOT / "fonts" / "NotoSansJP-Medium.ttf"

COLOURS = {
    "a": {
        "name": "海の青",
        "stops": (("0%", "#5FD8EC"), ("50%", "#1595C4"), ("100%", "#0B5E73")),
        "word": "#0B2E3D",
        "dark": "#0B2E3D",
    },
    "b": {
        "name": "藍の青",
        "stops": (("0%", "#4FC8F5"), ("50%", "#1F63D6"), ("100%", "#122E6B")),
        "word": "#12224F",
        "dark": "#0B1B3D",
    },
}


def final_icon(gradient_id: str) -> str:
    return icon_v2(
        gradient_id, tri_dx=FINAL_TRI_DX, tri_scale=FINAL_TRI_SCALE
    )


def word_path(word: Wordmark, x: float, baseline: float, cap: float, fill: str) -> tuple[str, float]:
    path, width, _ = word.outline(x, baseline, cap)
    return f'<path d="{path}" fill="{fill}"/>', width


def write_icon(variant: str) -> None:
    filename = f"natobe-{variant}-icon.svg"
    gid = f"natobe_{variant}_icon_gradient"
    doc = svg_document(120, 120, gradient(gid, COLOURS[variant]["stops"]), final_icon(gid))
    (OUT_DIR / filename).write_text(doc, encoding="utf-8")


def write_lockup(variant: str, word: Wordmark, *, white: bool = False) -> None:
    suffix = "-white" if white else ""
    filename = f"natobe-{variant}-lockup{suffix}.svg"
    gid = f"natobe_{variant}_lockup{suffix.replace('-', '_')}_gradient"
    cap = 70.0
    icon_size = cap * ICON_TO_CAP
    baseline = icon_size / 2 + cap / 2
    word_x = icon_size * (1 + ICON_GAP)
    fill = "#FFFFFF" if white else COLOURS[variant]["word"]
    path, word_width = word_path(word, word_x, baseline, cap, fill)
    icon = f'<g transform="scale({fmt(icon_size / 120)})">{final_icon(gid)}</g>'
    doc = svg_document(word_x + word_width, icon_size, gradient(gid, COLOURS[variant]["stops"]), icon + path)
    (OUT_DIR / filename).write_text(doc, encoding="utf-8")


def write_stack(variant: str, word: Wordmark) -> None:
    filename = f"natobe-{variant}-stack.svg"
    gid = f"natobe_{variant}_stack_gradient"
    icon_size = 120.0
    cap = icon_size / ICON_TO_CAP
    gap = icon_size * 0.22
    baseline = icon_size + gap + cap
    _, word_width = word_path(word, 0, baseline, cap, COLOURS[variant]["word"])
    width = max(icon_size, word_width)
    icon_x = (width - icon_size) / 2
    path, _ = word_path(word, (width - word_width) / 2, baseline, cap, COLOURS[variant]["word"])
    body = f'<g transform="translate({fmt(icon_x)} 0)">{final_icon(gid)}</g>' + path
    doc = svg_document(width, baseline + 2, gradient(gid, COLOURS[variant]["stops"]), body)
    (OUT_DIR / filename).write_text(doc, encoding="utf-8")


def write_avatar(variant: str, *, dark: bool = False) -> None:
    tone = "dark" if dark else "light"
    filename = f"natobe-{variant}-avatar-{tone}.svg"
    gid = f"natobe_{variant}_avatar_{tone}_gradient"
    # A 78%-diameter icon canvas keeps every hexagon vertex safe in a circular crop.
    icon_size = 512 * 0.78
    offset = (512 - icon_size) / 2
    background = COLOURS[variant]["dark"] if dark else "#FFFFFF"
    body = (
        f'<rect width="512" height="512" fill="{background}"/>'
        f'<g transform="translate({fmt(offset)} {fmt(offset)}) scale({fmt(icon_size / 120)})">'
        f'{final_icon(gid)}</g>'
    )
    doc = svg_document(512, 512, gradient(gid, COLOURS[variant]["stops"]), body)
    (OUT_DIR / filename).write_text(doc, encoding="utf-8")


def inline_lockup(word: Wordmark, spelling: str) -> str:
    cap = 52.0
    icon_size = cap * ICON_TO_CAP
    baseline = icon_size / 2 + cap / 2
    word_x = icon_size * (1 + ICON_GAP)
    path, width = word_path(word, word_x, baseline, cap, COLOURS["a"]["word"])
    gid = f"compare_{spelling.lower()}_gradient"
    return (
        f'<svg viewBox="0 0 {fmt(word_x + width)} {fmt(icon_size)}" aria-label="{spelling}" role="img">'
        f'<defs>{gradient(gid, COLOURS["a"]["stops"])}</defs>'
        f'<g transform="scale({fmt(icon_size / 120)})">{final_icon(gid)}</g>{path}</svg>'
    )


def write_sheet(word: Wordmark) -> None:
    old_word = Wordmark("Outfit-SemiBold.ttf", "Natobee", 0.015)
    font_data = base64.b64encode(FONT_FILE.read_bytes()).decode("ascii")

    def colour_section(v: str) -> str:
        c = COLOURS[v]
        return f'''<section><h2>カラー{v.upper()}案｜{c["name"]}</h2>
<div class="showcase"><img class="hero-icon" src="natobe-{v}-icon.svg"><img class="hero-lockup" src="natobe-{v}-lockup.svg"><img class="hero-stack" src="natobe-{v}-stack.svg"></div>
<div class="dark-band" style="background:{c['dark']}"><span>濃い背景での表示</span><img src="natobe-{v}-lockup-white.svg"></div></section>'''

    sns_groups = "".join(
        f'''<div class="sns-group"><strong>{v.upper()}案</strong>
<div class="circle"><img src="natobe-{v}-avatar-light.svg"></div><span>128px</span>
<div class="circle small"><img src="natobe-{v}-avatar-light.svg"></div><span>64px</span>
<div class="circle"><img src="natobe-{v}-avatar-dark.svg"></div><span>128px</span>
<div class="circle small"><img src="natobe-{v}-avatar-dark.svg"></div><span>64px</span></div>'''
        for v in COLOURS
    )
    small_groups = "".join(
        f'<div class="small-group"><strong>{v.upper()}案</strong>' + "".join(
            f'<img src="natobe-{v}-icon.svg" width="{size}" height="{size}"><span>{size}px</span>'
            for size in (48, 32, 16)
        ) + "</div>" for v in COLOURS
    )
    colour_cards = "".join(
        f'''<div class="colour-card"><strong>{v.upper()}案｜{c["name"]}</strong><div class="bar" style="background:linear-gradient(90deg,{c['stops'][0][1]},{c['stops'][1][1]},{c['stops'][2][1]})"></div>
<code>{"　".join(stop[1] for stop in c['stops'])}</code></div>''' for v, c in COLOURS.items()
    )
    html = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=1080"><title>株式会社ナトビー ロゴ｜最終案</title>
<style>
@font-face{{font-family:NotoJP;src:url(data:font/ttf;base64,{font_data}) format("truetype");font-weight:500}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;background:#fff;color:#0B2E3D;font-family:NotoJP,sans-serif}}main{{width:1080px;overflow:hidden}}
header,section{{padding:36px 60px}}header{{padding-top:46px;border-bottom:1px solid #dbe7ea}}h1{{font-size:34px;margin:0 0 9px}}header p{{margin:0;color:#5c7680}}section+section{{border-top:1px solid #dbe7ea}}h2{{font-size:27px;margin:0 0 24px}}
.fix-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.fix-card{{border:1px solid #dbe7ea;border-radius:14px;padding:18px;text-align:center;min-width:0}}.fix-card h3{{margin:0 0 14px;font-size:18px}}.fix-card svg{{display:block;width:100%;height:96px}}.icon-row{{display:flex;justify-content:center;align-items:center;gap:24px}}.icon-row svg{{width:200px;height:200px}}
.showcase{{height:230px;display:grid;grid-template-columns:210px 1fr 180px;gap:28px;align-items:center}}.hero-icon{{width:200px}}.hero-lockup{{width:430px;max-width:100%}}.hero-stack{{height:200px;max-width:100%}}.dark-band{{margin:12px -60px -36px;padding:28px 60px;display:flex;align-items:center;gap:42px;color:#fff}}.dark-band span{{width:155px;font-size:14px;opacity:.8}}.dark-band img{{width:510px;max-height:95px}}
.preview{{background:#f5f9fa}}.sns-group,.small-group{{background:#fff;border:1px solid #dbe7ea;border-radius:14px;padding:20px;display:flex;align-items:center;gap:12px;margin-top:16px}}.sns-group strong,.small-group strong{{width:55px}}.circle{{width:128px;height:128px;border-radius:50%;overflow:hidden;box-shadow:inset 0 0 0 1px #dbe7ea}}.circle.small{{width:64px;height:64px}}.circle img{{width:100%;height:100%;display:block}}.sns-group span,.small-group span{{font-size:12px;color:#637b84}}
.small-group img{{display:block;margin-left:18px}}.colours{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.colour-card{{border:1px solid #dbe7ea;border-radius:14px;padding:20px}}.bar{{height:52px;border-radius:10px;margin:14px 0 10px}}code{{font-size:13px;color:#58717a}}
</style></head><body><main><header><h1>株式会社ナトビー ロゴ｜最終案</h1><p>六角形＋Natobe で確定。色をA案・B案から選んでください</p></header>
<section><h2>直したところ</h2><div class="fix-grid"><div class="fix-card"><h3>前｜綴り</h3>{inline_lockup(old_word, "Natobee")}</div><div class="fix-card"><h3>後｜綴り</h3>{inline_lockup(word, "Natobe")}</div>
<div class="fix-card"><h3>前｜アイコン</h3><div class="icon-row"><svg viewBox="0 0 120 120"><defs>{gradient("old_icon_gradient", COLOURS["a"]["stops"])}</defs>{icon_v2("old_icon_gradient")}</svg></div></div>
<div class="fix-card"><h3>後｜アイコン</h3><div class="icon-row"><svg viewBox="0 0 120 120"><defs>{gradient("new_icon_gradient", COLOURS["a"]["stops"])}</defs>{final_icon("new_icon_gradient")}</svg></div></div></div></section>
{colour_section("a")}{colour_section("b")}
<section class="preview"><h2>SNSのアイコンにした時</h2>{sns_groups}</section>
<section class="preview"><h2>小さくした時の見え方</h2>{small_groups}</section>
<section><h2>使用カラー</h2><div class="colours">{colour_cards}</div></section></main></body></html>'''
    (OUT_DIR / "sheet.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    word = Wordmark("Outfit-SemiBold.ttf", "Natobe", 0.015)
    for variant in COLOURS:
        write_lockup(variant, word)
        write_lockup(variant, word, white=True)
        write_stack(variant, word)
        write_icon(variant)
        write_avatar(variant)
        write_avatar(variant, dark=True)
    write_sheet(word)


if __name__ == "__main__":
    main()
