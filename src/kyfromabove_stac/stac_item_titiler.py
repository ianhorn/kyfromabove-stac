"""
This python script creates a function that will be used to populate
stac-item variables.

It will then use the titiler.extension to create a stac item

Based on stac.py from which basically is rio-stac Extension.
"""
import os
import json
import requests
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pystac

from constants_titiler import assign_datetime, assign_collection

# --- Configuration ---
TITILER_ENDPOINT = "http://localhost:8000/cog/stac"
ITEM_COLLECTION = "orthos-phase2"
CSV_PATH = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{ITEM_COLLECTION}.csv"
STAC_API_URL = f"https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/{ITEM_COLLECTION}/items"
THUMBNAIL_FOLDER = f"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/{ITEM_COLLECTION}"
ITEM_OUTPUT_DIR = Path(f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items_v1.1.0/{ITEM_COLLECTION}")
max_workers = 16
# --- Load URLs ---
urls = pd.read_csv(CSV_PATH)['aws_url'].dropna().tolist()

# --- Asset Creators ---
def get_tfw_asset(url):
    if not "Phase3" in url:
        return None
    else:
        return {
            "href": os.path.splitext(url)[0] + ".tfw",
            "title": "world file",
            "type": "text/plain",
            "roles": ["metadata"],
        }

def get_thumbnail_asset(url):
    name = Path(url).stem + ".png"
    return {
        "href": f"{THUMBNAIL_FOLDER}/{name}",
        "title": "thumbnail",
        "type": "image/png",
        "roles": ["thumbnail"],
    }

# --- STAC Fixers ---
def fix_band_descriptions(item):
    data_asset = item.get("assets", {}).get("data", {})
    eo_bands = data_asset.get("eo:bands")
    if eo_bands:
        item.setdefault("properties", {})["eo:bands"] = eo_bands
        for band in eo_bands:
            if band.get("description", "").lower() == "undefined":
                band["description"] = "infrared"

def fix_datetime(item):
    props = item.get("properties", {})
    if props.get("datetime") is None and props.get("start_datetime"):
        props["datetime"] = props["start_datetime"]

# --- Item Creation ---
def create_stac_item(url):
    datetime_str = assign_datetime(url)
    collection = assign_collection(url)
    params = {
        "url": url,
        "datetime": datetime_str,
        "collection": collection,
        "asset_media_type": "image/tiff; application=geotiff; profile=cloud-optimized",
        "asset_roles": ["data", "visual"],
    }

    try:
        response = requests.get(TITILER_ENDPOINT, params=params)
        if not response.ok:
            print(f"❌ Failed to process {url}: {response.status_code} {response.text}")
            return

        item = response.json()
        fix_band_descriptions(item)
        fix_datetime(item)
        item.setdefault("assets", {})
        item["assets"]["thumbnail"] = get_thumbnail_asset(url)
        tfw_asset = get_tfw_asset(url)
        if tfw_asset:
            item["assets"]["metadata"] = tfw_asset

        # Validate STAC
        try:
            pystac.Item.from_dict(item).validate()
            print("✅ STAC item validated successfully.")
        except Exception as e:
            print(f"❌ STAC item validation failed: {e}")
            return

        # Post to STAC API
        try:
            post = requests.post(STAC_API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(item))
            if post.ok:
                print("✅ STAC item posted successfully.")
            else:
                print(f"❌ Failed to post STAC item: {post.status_code} {post.text}")
        except Exception as e:
            print(f"❌ Error posting to STAC API: {e}")

        # Write to disk
        output_path = ITEM_OUTPUT_DIR / f"{Path(url).stem}.json"
        if not output_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(item, f, indent=2)
            print(f"✅ Item written to {output_path}")
        else:
            print(f"⚠️ Skipping existing item: {output_path}")

    except Exception as e:
        print(f"❌ Unexpected error for {url}: {e}")

# --- Main ---
def main(urls_to_process=None):
    if urls_to_process is None:
        urls_to_process = urls
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(create_stac_item, url): url for url in urls_to_process}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"❌ Exception processing {futures[future]}: {e}")

if __name__ == "__main__":
    # For full batch run:
    main()

    # For single test run:
    # main([
    #     "https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2024_Season1_3IN/N203E093_2024_Season1_3IN_cog.tif"
    # ])