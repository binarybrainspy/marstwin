"""Download the NASA reference imagery used by the MarsTwin frontend.

Assets are public NASA images. Credits are written to
apps/web/public/images/credits.json and surfaced in the UI footer.

Usage (from repo root):
  python science/scripts/fetch_nasa_imagery.py
  python science/scripts/fetch_nasa_imagery.py --force
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "apps" / "web" / "public" / "images"
API = "https://images-api.nasa.gov/search"

ASSETS = {
    "hero-mars": {
        "id": "PIA20332",
        "file": "hero-mars.jpg",
        "role": "Mars panorama hero",
        "prefer": ["large", "orig", "medium"],
    },
    "target-mars": {
        "id": "PIA24096",
        "file": "target-mars.jpg",
        "role": "Jezero Crater target",
        "prefer": ["large", "orig", "medium"],
    },
    "target-moon": {
        "id": "PIA00001",
        "file": "target-moon.jpg",
        "role": "Lunar south pole target",
        "prefer": ["large", "orig", "medium"],
    },
    "analog-dry-valleys": {
        "id": "PIA12461",
        "file": "analog-dry-valleys.jpg",
        "role": "McMurdo Dry Valleys known analog",
        "prefer": ["large", "orig", "medium"],
    },
    "analog-atacama": {
        "id": "PIA23420",
        "file": "analog-atacama.jpg",
        "role": "Atacama Desert known analog",
        "prefer": ["orig", "large", "medium"],
    },
}


def fetch_json(url: str, timeout: int = 60, attempts: int = 4) -> dict:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "MarsTwin/0.1"}
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"NASA API unavailable after {attempts} attempts: {last}")


def fetch_bytes(url: str, timeout: int = 120, attempts: int = 4) -> bytes:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "MarsTwin/0.1"}
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                data = response.read()
            if not content_type.startswith("image/") or len(data) < 2000:
                raise RuntimeError(
                    f"unexpected image response: {content_type}, {len(data)} bytes"
                )
            return data
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"image unavailable after {attempts} attempts: {last}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch NASA reference imagery")
    parser.add_argument("--force", action="store_true", help="Refetch existing images")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    credits: dict[str, object] = {
        "provider": "NASA Image and Video Library",
        "note": "NASA imagery is generally not copyrighted; individual credits are listed per asset.",
        "assets": {},
    }

    for key, asset in ASSETS.items():
        nasa_id = asset["id"]
        path = OUT / asset["file"]
        try:
            result = fetch_json(f"{API}?nasa_id={nasa_id}")
            item = result["collection"]["items"][0]
            data = item["data"][0]
            if path.exists() and not args.force:
                print(f"  cached {asset['file']}")
            else:
                links = [link["href"] for link in item.get("links", [])]
                chosen = None
                for size in asset["prefer"]:
                    chosen = next(
                        (link for link in links if link.lower().endswith(f"~{size}.jpg")),
                        None,
                    )
                    if chosen:
                        break
                if chosen is None and links:
                    chosen = links[0]
                if chosen is None:
                    raise RuntimeError(f"no image link for {nasa_id}")
                path.write_bytes(fetch_bytes(chosen))
                print(f"  {asset['file']} <- {chosen.rsplit('/', 1)[-1]}")
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            print(f"  FAILED {asset['file']}: {exc}")
            continue

        credits["assets"][key] = {
            "file": f"/images/{asset['file']}",
            "nasaId": nasa_id,
            "title": data.get("title"),
            "credit": data.get("secondary_creator") or data.get("center") or "NASA",
            "center": data.get("center"),
            "dateCreated": data.get("date_created"),
            "source": f"https://images.nasa.gov/details/{nasa_id}",
            "role": asset["role"],
        }

    (OUT / "credits.json").write_text(json.dumps(credits, indent=2), encoding="utf-8")
    print(f"Credits -> {OUT / 'credits.json'}")


if __name__ == "__main__":
    main()
