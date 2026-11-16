"""Fetch Earth site thumbnails and a world locator from Esri World Imagery.

Writes static JPEGs into apps/web/public/images so the frontend ships with
imagery. No API key is required; attribution is included in the UI and in
images/sources.json.

Usage (from repo root):
  python science/scripts/fetch_site_imagery.py
  python science/scripts/fetch_site_imagery.py --force
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCIENCE = ROOT / "science"
OUT = ROOT / "apps" / "web" / "public" / "images"
sys.path.insert(0, str(SCIENCE))

from lib.io_util import load_cells  # noqa: E402

EXPORT = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/export"
)
WORLD_EXPORT = EXPORT
ATTRIBUTION = "Esri, Maxar, Earthstar Geographics"
EARTH_RADIUS_M = 6378137.0


def mercator(lat: float, lon: float) -> tuple[float, float]:
    x = EARTH_RADIUS_M * math.radians(lon)
    y = EARTH_RADIUS_M * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def fetch_image(url: str, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "MarsTwin/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if not content_type.startswith("image/") or len(data) < 2000:
        raise RuntimeError(f"unexpected imagery response: {content_type}, {len(data)} bytes")
    return data


def export_url(
    bbox: tuple[float, float, float, float],
    size: tuple[int, int],
    sr: int = 3857,
) -> str:
    params = {
        "bbox": ",".join(f"{value:.2f}" for value in bbox),
        "bboxSR": sr,
        "imageSR": sr,
        "size": f"{size[0]},{size[1]}",
        "format": "jpg",
        "f": "image",
    }
    return f"{EXPORT}?{urllib.parse.urlencode(params)}"


def site_bbox(lat: float, lon: float, box_km: float) -> tuple[float, float, float, float]:
    x, y = mercator(lat, lon)
    half_w = box_km * 1000 / 2
    half_h = half_w * 0.625  # 1.6:1 card image
    return (x - half_w, y - half_h, x + half_w, y + half_h)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Esri satellite thumbnails")
    parser.add_argument("--force", action="store_true", help="Refetch existing images")
    parser.add_argument("--box-km", type=float, default=36.0, help="Image width in km")
    parser.add_argument("--size", default="640x400", help="Widthxheight, e.g. 640x400")
    parser.add_argument("--skip-world", action="store_true", help="Skip world.jpg")
    args = parser.parse_args()

    try:
        width, height = (int(v) for v in args.size.lower().split("x"))
    except ValueError as exc:
        raise SystemExit("--size must look like 640x400") from exc

    sites_dir = OUT / "sites"
    sites_dir.mkdir(parents=True, exist_ok=True)
    cells = load_cells()

    sources: dict[str, object] = {
        "attribution": ATTRIBUTION,
        "provider": "Esri World Imagery",
        "note": "Satellite context imagery; not used in the numerical score.",
        "sites": {},
    }

    fetched = 0
    skipped = 0
    failed: list[str] = []
    for cell in cells:
        path = sites_dir / f"{cell['id']}.jpg"
        if path.exists() and not args.force:
            skipped += 1
            continue
        bbox = site_bbox(cell["lat"], cell["lon"], args.box_km)
        try:
            data = fetch_image(export_url(bbox, (width, height)))
            path.write_bytes(data)
            fetched += 1
            print(f"  site image {cell['id']} ({len(data) // 1024} KB)")
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            failed.append(cell["id"])
            print(f"  FAILED {cell['id']}: {exc}")
        sources["sites"][cell["id"]] = {
            "file": f"/images/sites/{cell['id']}.jpg",
            "lat": cell["lat"],
            "lon": cell["lon"],
            "boxKm": args.box_km,
        }
        time.sleep(0.15)

    if not args.skip_world:
        world_path = OUT / "world.jpg"
        if args.force or not world_path.exists():
            bbox = (
                -EARTH_RADIUS_M * math.pi,
                -EARTH_RADIUS_M * math.pi,
                EARTH_RADIUS_M * math.pi,
                EARTH_RADIUS_M * math.pi,
            )
            try:
                data = fetch_image(export_url(bbox, (2048, 2048)))
                world_path.write_bytes(data)
                print(f"  world image ({len(data) // 1024} KB)")
            except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
                print(f"  FAILED world image: {exc}")
        sources["world"] = "/images/world.jpg"

    (OUT / "sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    print(
        f"Images: {fetched} fetched, {skipped} cached, {len(failed)} failed "
        f"-> {OUT}"
    )
    if failed:
        print("Failed ids:", ", ".join(failed))


if __name__ == "__main__":
    main()
