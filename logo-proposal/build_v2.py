#!/usr/bin/env python3
"""Generate the Natobe v2 icon balance proposals described in SPEC-v2.md."""

from __future__ import annotations

from pathlib import Path

from build import (
    B_HEXAGON,
    B_STOPS,
    B_TRIANGLE,
    Wordmark,  # Re-export the shared outline utility for future v2 lockups.
    fmt,
    gradient,
    rounded_polygon,
    svg_document,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out" / "v2"
POINTY_HEXAGON = [(60, 4), (111, 32), (111, 88), (60, 116), (9, 88), (9, 32)]


def _transform_about_centroid(
    points: list[tuple[float, float]], scale: float, dx: float, dy: float
) -> list[tuple[float, float]]:
    centroid_x = sum(x for x, _ in points) / len(points)
    centroid_y = sum(y for _, y in points) / len(points)
    return [
        (
            centroid_x + (x - centroid_x) * scale + dx,
            centroid_y + (y - centroid_y) * scale + dy,
        )
        for x, y in points
    ]


def icon_v2(
    gradient_id: str,
    *,
    tri_scale: float = 1.0,
    tri_dx: float = 0.0,
    tri_dy: float = 0.0,
    hex_points: list[tuple[float, float]] = B_HEXAGON,
    hex_r: float = 12,
    tri_r: float = 3,
) -> str:
    """Return a parameterized hexagon and play-mark SVG fragment."""
    triangle = _transform_about_centroid(B_TRIANGLE, tri_scale, tri_dx, tri_dy)
    return (
        f'<path d="{rounded_polygon(hex_points, hex_r)}" fill="url(#{gradient_id})"/>'
        f'<path d="{rounded_polygon(triangle, tri_r)}" fill="#FFFFFF"/>'
    )


VARIANTS = (
    {},
    {"tri_scale": 1.12},
    {"tri_dx": -7.5},
    {"tri_dx": -3.75, "tri_scale": 1.06},
    {"hex_points": POINTY_HEXAGON},
    {"hex_r": 20, "tri_scale": 1.08},
)


def write_icons() -> None:
    for index, parameters in enumerate(VARIANTS):
        gradient_id = f"icon_v{index}_gradient"
        document = svg_document(
            120,
            120,
            gradient(gradient_id, B_STOPS),
            icon_v2(gradient_id, **parameters),
        )
        (OUT_DIR / f"icon-v{index}.svg").write_text(document, encoding="utf-8")


def write_variants_sheet() -> None:
    rows = "\n".join(
        f"""<div class="variant">
  <div class="label">v{index}</div>
  <img src="icon-v{index}.svg" width="220" height="220" alt="v{index} at 220px">
  <img src="icon-v{index}.svg" width="96" height="96" alt="v{index} at 96px">
  <div class="sns"><img src="icon-v{index}.svg" width="96" height="96" alt="v{index} circular preview"></div>
  <img src="icon-v{index}.svg" width="48" height="48" alt="v{index} at 48px">
</div>"""
        for index in range(len(VARIANTS))
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080">
<title>Natobe icon v2 variants</title>
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: 1080px; background: #fff; color: #0B2E3D; }}
body {{ font-family: Arial, sans-serif; }}
main {{ width: 1080px; padding: 0 52px; background: #fff; }}
.variant {{
  min-height: 252px;
  display: grid;
  grid-template-columns: 56px 220px 96px 96px 48px;
  column-gap: 46px;
  align-items: center;
  border-bottom: 1px solid #dbe7ea;
}}
.label {{ font-size: 22px; font-weight: 700; }}
img {{ display: block; }}
.sns {{ width: 96px; height: 96px; overflow: hidden; border-radius: 50%; }}
</style>
</head>
<body><main>
{rows}
</main></body>
</html>
"""
    (OUT_DIR / "variants.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_icons()
    write_variants_sheet()


if __name__ == "__main__":
    main()
