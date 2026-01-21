"""
This script creates STAC items for KyFromAbove DEMs (Phase3),
using titiler extension to generate items.
"""

import os
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import pystac

from constants_titiler import assign_datetime, assign_collection

# --- Configuration ---
TITILER_ENDPOINT = "https://6hp4guqpwe.execute-api.us-west-2.amazonaws.com/cog/stac"
ITEM_COLLECTION = "dem-phase3"
CSV_PATH = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{ITEM_COLLECTION}.csv"
STAC_API_URL = f"https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/{ITEM_COLLECTION}/items"
THUMBNAIL_FOLDER = f"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/{ITEM_COLLECTION}"
ITEM_OUTPUT_DIR = Path(f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/{ITEM_COLLECTION}")
MAX_WORKERS = 16

# --- Load URLs ---
urls = pd.read_csv(CSV_PATH)['aws_url'].dropna().tolist()

# --- Asset Creators ---
def get_thumbnail_asset(url):
    name = Path(url).stem + ".png"
    return {
        "href": f"{THUMBNAIL_FOLDER}/{name}",
        "title": "thumbnail",
        "type": "image/png",
        "roles": ["thumbnail"],
    }

# --- Helpers ---
def normalize_datetime(dt_str: str) -> str:
    """
    Convert start date of a range or single date to UTC ISO format with 'Z'.
    """
    if "/" in dt_str:
        dt_str = dt_str.split("/")[0]  # pick start of range
    from datetime import datetime, timezone
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

# --- STAC Item Creation ---
def create_stac_item(url: str):
    try:
        datetime_str = normalize_datetime(assign_datetime(url))
        collection = assign_collection(url)

        # --- Request STAC item from Titiler ---
        params = {
            "url": url,
            "asset_name": "data",
            "asset_media_type": "image/tiff; application=geotiff; profile=cloud-optimized",
            "with_proj": True,
            "with_raster": True,
            "max_size": 1024,
            "geometry_densify": 0,
            "geometry_precision": -1,
        }
        response = requests.get(TITILER_ENDPOINT, params=params)
        response.raise_for_status()
        item = response.json()

        # --- Add DEM-specific properties ---
        item.setdefault("properties", {})
        item["properties"]["datetime"] = datetime_str
        item["properties"]["license"] = "CC-BY-4.0"
        item["collection"] = collection

        # --- Add thumbnail ---
        item.setdefault("assets", {})
        item["assets"]["thumbnail"] = get_thumbnail_asset(url)

        # --- Validate STAC item ---
        try:
            pystac.Item.from_dict(item).validate()
            print(f"✅ Validated: {url}")
        except Exception as e:
            print(f"❌ Validation failed: {url} | {e}")
            return

        # --- Post to STAC API ---
        try:
            post = requests.post(STAC_API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(item))
            if post.ok:
                print(f"✅ Posted: {url}")
            else:
                print(f"❌ Post failed ({post.status_code}): {url} | {post.text}")
        except Exception as e:
            print(f"❌ Error posting {url}: {e}")

        # --- Save locally ---
        output_path = ITEM_OUTPUT_DIR / f"{Path(url).stem}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2)
        print(f"✅ Saved locally: {output_path}")

    except Exception as e:
        print(f"❌ Unexpected error for {url}: {e}")

# --- Main ---
def main(urls_to_process=None):
    if urls_to_process is None:
        urls_to_process = urls

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(create_stac_item, url): url for url in urls_to_process}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"❌ Exception processing {futures[future]}: {e}")

if __name__ == "__main__":
    main()
    