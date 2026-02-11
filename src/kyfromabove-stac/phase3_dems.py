"""
CSV-to-STAC pipeline using Titiler for geometry and bbox.
End result matches your cURL example format.
Adds thumbnail and minimal links, no local raster needed.
"""

import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
from threading import Lock
# from constants_titiler import assign_collection

# --- Configuration ---
CSV_FILE = Path("C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/dem-phase3.csv")
OUTPUT_DIR = Path("C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/dem-phase3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TITILER_ENDPOINT = "https://6hp4guqpwe.execute-api.us-west-2.amazonaws.com/cog/stac"
THUMBNAIL_BASE = "https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/dem-phase3"
HARDCODED_DATETIME = "2025-03-03T00:00:00Z"
HARDCODED_END_DATETIME = "2025-03-08T00:00:00Z"

# Thread-safe print
print_lock = Lock()
def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

# --- Load CSV ---
data = pd.read_csv(CSV_FILE)
safe_print(f"Loaded {len(data)} rows from {CSV_FILE}")

# --- Create STAC item for a single URL ---
def create_stac_item(url: str):
    try:
        item_id = Path(url).name
        # collection = assign_collection(url) or "dem-phase3"

        # --- Call Titiler to get geometry and bbox ---
        params = {"url": url, "with_eo": "false", "asset_roles": "data"}
        response = requests.get(TITILER_ENDPOINT, params=params, timeout=60)
        response.raise_for_status()
        tiler_item = response.json()

        # Extract geometry and bbox
        geometry = tiler_item.get("geometry")
        bbox = tiler_item.get("bbox")

        # --- Construct STAC item ---
        item = {
            "type": "Feature",
            "stac_version": "1.0.0",
            "stac_extensions": [
                "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
                "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
            ],
            "id": item_id,
            "geometry": geometry,
            "bbox": bbox,
            "properties": {
                "license": "CC-BY-4.0",
                "proj:epsg": tiler_item["properties"].get("proj:epsg", 3089),
                "proj:geometry": tiler_item["properties"].get("proj:geometry"),
                "proj:bbox": tiler_item["properties"].get("proj:bbox"),
                "proj:shape": tiler_item["properties"].get("proj:shape"),
                "proj:transform": tiler_item["properties"].get("proj:transform"),
                "start_datetime": HARDCODED_DATETIME,
                "end_datetime": HARDCODED_END_DATETIME,
                "datetime": HARDCODED_DATETIME
            },
            "links": [
                # {"rel": "collection", "href": collection, "type": "application/json"}
            ],
            "assets": {
                "asset": {
                    "href": url,
                    "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    "raster:bands": tiler_item.get("assets", {}).get("asset", {}).get("raster:bands", []),
                    "roles": ["data", "visual"]
                },
                "thumbnail": {
                    "href": f"{THUMBNAIL_BASE}/{Path(url).stem}.png",
                    "type": "image/png",
                    "roles": ["thumbnail"],
                    "title": "Thumbnail image"
                }
            }
            # "collection": collection
        }

        # --- Save locally ---
        file_path = OUTPUT_DIR / f"{Path(url).stem}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2)

        safe_print(f"✅ STAC item created and saved for: {url}")
        return item

    except Exception as e:
        safe_print(f"❌ Failed processing {url}: {e}")
        return None

# --- Main execution ---
def main(max_workers: int = 24):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(create_stac_item, row["aws_url"]): idx for idx, row in data.iterrows()}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                safe_print(f"❌ Exception in worker {futures[future]}: {e}")

if __name__ == "__main__":
    main()