#!/usr/bin/env python3
"""Build the approved Natobe A-colour logo delivery package."""

from __future__ import annotations

import base64
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "out" / "v3"
FINAL_DIR = ROOT / "final"
PNG_DIR = FINAL_DIR / "png"
FONT_FILE = ROOT / "fonts" / "NotoSansJP-Medium.ttf"
CHROME = "google-chrome"

SVG_FILES = {
    "natobe-a-lockup.svg": "natobe-logo.svg",
    "natobe-a-lockup-white.svg": "natobe-logo-white.svg",
    "natobe-a-stack.svg": "natobe-logo-stack.svg",
    "natobe-a-icon.svg": "natobe-icon.svg",
    "natobe-a-avatar-light.svg": "natobe-avatar-light.svg",
    "natobe-a-avatar-dark.svg": "natobe-avatar-dark.svg",
}


def svg_dimensions(path: Path) -> tuple[float, float]:
    root = ET.parse(path).getroot()
    view_box = root.get("viewBox")
    if not view_box:
        raise ValueError(f"SVG has no viewBox: {path}")
    values = view_box.replace(",", " ").split()
    if len(values) != 4:
        raise ValueError(f"Invalid viewBox in {path}: {view_box!r}")
    width, height = float(values[2]), float(values[3])
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid viewBox dimensions in {path}: {view_box!r}")
    return width, height


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as png:
        header = png.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a valid PNG: {path}")
    return struct.unpack(">II", header[16:24])


def screenshot(html_path: Path, output: Path, width: int, height: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        CHROME,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--hide-scrollbars",
        "--default-background-color=00000000",
        f"--window-size={width},{height}",
        f"--screenshot={output}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    actual = png_dimensions(output)
    if actual != (width, height):
        raise RuntimeError(
            f"Unexpected PNG size for {output}: {actual[0]}x{actual[1]} "
            f"(expected {width}x{height})"
        )


def rasterize_svg(svg_path: Path, output: Path, width: int, height: int | None = None) -> None:
    view_width, view_height = svg_dimensions(svg_path)
    if height is None:
        height = round(width * view_height / view_width)
    html = (
        "<style>html,body{margin:0;padding:0;background:transparent}"
        "img{display:block;width:100%;height:auto}</style>"
        f'<img src="{svg_path.resolve().as_uri()}">'
    )
    with tempfile.TemporaryDirectory(prefix="natobe-final-") as temp_dir:
        html_path = Path(temp_dir) / "render.html"
        html_path.write_text(html, encoding="utf-8")
        screenshot(html_path, output, width, height)


def delivery_html() -> str:
    font_data = base64.b64encode(FONT_FILE.read_bytes()).decode("ascii")
    logo = (FINAL_DIR / "natobe-logo.svg").resolve().as_uri()
    white = (FINAL_DIR / "natobe-logo-white.svg").resolve().as_uri()
    stack = (FINAL_DIR / "natobe-logo-stack.svg").resolve().as_uri()
    light = (FINAL_DIR / "natobe-avatar-light.svg").resolve().as_uri()
    dark = (FINAL_DIR / "natobe-avatar-dark.svg").resolve().as_uri()
    icon = (FINAL_DIR / "natobe-icon.svg").resolve().as_uri()
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>Natobe ロゴ 最終版</title>
<style>
@font-face{{font-family:NotoJP;src:url(data:font/ttf;base64,{font_data}) format("truetype");font-weight:500}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1080px;background:#eef5f7;color:#0B2E3D;font-family:NotoJP,sans-serif}}
main{{width:1080px}}header{{height:150px;padding:42px 60px;background:#fff;border-bottom:1px solid #d6e4e8}}
h1{{margin:0;font-size:38px;line-height:1.5;font-weight:500}}section{{padding:34px 60px;background:#fff;border-bottom:1px solid #d6e4e8}}
h2{{margin:0 0 26px;font-size:29px;line-height:1.4;font-weight:500}}.center{{display:flex;align-items:center;justify-content:center}}
.basic{{height:380px}}.basic img,.reverse img{{width:880px}}.reverse{{height:380px;background:#0B2E3D;color:#fff}}
.stack{{height:570px}}.stack img{{width:420px}}.sns{{height:390px}}.sns-row{{display:flex;justify-content:center;gap:90px}}
.sns img{{display:block;width:220px;height:220px;border-radius:50%}}.favicon{{height:210px}}.favicon-row{{display:flex;align-items:end;justify-content:center;gap:70px;height:80px}}
.sample{{display:flex;align-items:center;gap:14px;font-size:24px;color:#536d76}}.sample img{{display:block}}.colours{{height:270px}}
.colour-row{{display:flex;justify-content:space-between;gap:24px}}.swatch{{display:flex;align-items:center;gap:16px;font-size:23px}}
.chip{{width:86px;height:86px;border-radius:10px;box-shadow:inset 0 0 0 1px rgba(11,46,61,.08)}}
</style></head><body><main>
<header><h1>Natobe ロゴ 最終版｜カラー＝海の青</h1></header>
<section class="basic"><h2>横型（基本）</h2><div class="center"><img src="{logo}"></div></section>
<section class="reverse"><h2>白抜き（濃い背景用）</h2><div class="center"><img src="{white}"></div></section>
<section class="stack"><h2>縦型</h2><div class="center"><img src="{stack}"></div></section>
<section class="sns"><h2>SNSアイコン</h2><div class="sns-row"><img src="{light}"><img src="{dark}"></div></section>
<section class="favicon"><h2>ファビコン</h2><div class="favicon-row">
<div class="sample"><img src="{icon}" width="64" height="64"><span>64px</span></div>
<div class="sample"><img src="{icon}" width="32" height="32"><span>32px</span></div>
<div class="sample"><img src="{icon}" width="16" height="16"><span>16px</span></div></div></section>
<section class="colours"><h2>使用カラー</h2><div class="colour-row">
<div class="swatch"><div class="chip" style="background:#5FD8EC"></div><span>#5FD8EC</span></div>
<div class="swatch"><div class="chip" style="background:#1595C4"></div><span>#1595C4</span></div>
<div class="swatch"><div class="chip" style="background:#0B5E73"></div><span>#0B5E73</span></div>
</div></section></main></body></html>'''


def build_delivery_preview() -> None:
    # The section heights above add up to the complete page height.
    preview_height = 2350
    with tempfile.TemporaryDirectory(prefix="natobe-preview-") as temp_dir:
        html_path = Path(temp_dir) / "delivery.html"
        html_path.write_text(delivery_html(), encoding="utf-8")
        screenshot(html_path, FINAL_DIR / "natobe-logo-delivery.png", 1080, preview_height)


def main() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, destination_name in SVG_FILES.items():
        shutil.copy2(SOURCE_DIR / source_name, FINAL_DIR / destination_name)

    rasterize_svg(FINAL_DIR / "natobe-logo.svg", PNG_DIR / "natobe-logo.png", 2000)
    rasterize_svg(FINAL_DIR / "natobe-logo-white.svg", PNG_DIR / "natobe-logo-white.png", 2000)
    rasterize_svg(FINAL_DIR / "natobe-logo-stack.svg", PNG_DIR / "natobe-logo-stack.png", 1200)
    rasterize_svg(FINAL_DIR / "natobe-icon.svg", PNG_DIR / "natobe-icon-1024.png", 1024, 1024)
    rasterize_svg(FINAL_DIR / "natobe-avatar-light.svg", PNG_DIR / "natobe-avatar-light-800.png", 800, 800)
    rasterize_svg(FINAL_DIR / "natobe-avatar-dark.svg", PNG_DIR / "natobe-avatar-dark-800.png", 800, 800)
    for size in (512, 180, 32):
        rasterize_svg(FINAL_DIR / "natobe-icon.svg", PNG_DIR / f"favicon-{size}.png", size, size)
    build_delivery_preview()


if __name__ == "__main__":
    main()
