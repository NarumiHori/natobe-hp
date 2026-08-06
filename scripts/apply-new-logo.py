#!/usr/bin/env python3
"""Apply Natobe's approved logo assets to the production and draft sites."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "logo-proposal" / "final"
HTML_PATHS = (
    ROOT / "deploy-prod" / "index.html",
    ROOT / "deploy-prod" / "company.html",
    ROOT / "deploy-prod" / "404.html",
    ROOT / "draft-v3" / "site" / "index.html",
    ROOT / "draft-v3" / "site" / "company.html",
)

LOGO_IMG = re.compile(
    r'<img\b[^>]*\bsrc="img/logo(?:-white)?\.svg"[^>]*>', re.IGNORECASE
)


def copy_svg(source_name: str, relative_destinations: tuple[str, ...]) -> None:
    source = SOURCE / source_name
    for relative in relative_destinations:
        destination = ROOT / relative
        if destination.parent.exists():
            shutil.copyfile(source, destination)


def update_logo_img(match: re.Match[str]) -> str:
    tag = match.group(0)
    tag = tag.replace('width="240" height="56"', 'width="491" height="120"')
    tag = tag.replace('alt="NATOBE"', 'alt="Natobe"')
    return tag


def update_html(path: Path) -> None:
    if not path.exists():
        return
    original = path.read_bytes()
    text = original.decode("utf-8")
    updated = LOGO_IMG.sub(update_logo_img, text)
    path.write_bytes(updated.encode("utf-8"))


def make_icons(site: Path, only_existing: bool = False) -> None:
    if not site.exists():
        return
    with Image.open(SOURCE / "png" / "favicon-512.png") as source_image:
        icon = source_image.convert("RGBA")
        favicon = site / "favicon.ico"
        if not only_existing or favicon.exists():
            icon.save(
                favicon,
                format="ICO",
                sizes=[(16, 16), (32, 32), (48, 48)],
            )

        for filename, size in (
            ("icon-192.png", 192),
            ("apple-touch-icon.png", 180),
        ):
            destination = site / filename
            if only_existing and not destination.exists():
                continue
            resized = icon.resize((size, size), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (size, size), "white")
            canvas.alpha_composite(resized)
            canvas.convert("RGB").save(destination, format="PNG")


def main() -> None:
    copy_svg(
        "natobe-logo.svg",
        ("deploy-prod/img/logo.svg", "draft-v3/site/img/logo.svg"),
    )
    copy_svg(
        "natobe-logo-white.svg",
        ("deploy-prod/img/logo-white.svg", "draft-v3/site/img/logo-white.svg"),
    )
    copy_svg("natobe-icon.svg", ("deploy-prod/favicon.svg",))
    draft_favicon = ROOT / "draft-v3" / "site" / "favicon.svg"
    if draft_favicon.exists():
        shutil.copyfile(SOURCE / "natobe-icon.svg", draft_favicon)

    for html_path in HTML_PATHS:
        update_html(html_path)

    make_icons(ROOT / "deploy-prod")
    make_icons(ROOT / "draft-v3" / "site", only_existing=True)


if __name__ == "__main__":
    main()
