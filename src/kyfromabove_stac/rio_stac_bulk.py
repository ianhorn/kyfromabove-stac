import os

# -----------------------------
# Environment
# -----------------------------
os.environ["PROJ_LIB"] = r"venv/Lib/site-packages/rasterio/proj_data"
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["CPL_VSIL_CURL_CACHE"] = "YES"

import json
import pandas as pd
from datetime import timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from rio_stac import create_stac_item
import pystac

from item_constants import (
    assign_start_datetime,
    assign_end_datetime,
    assign_collection,
    get_item_properties
)

# -----------------------------
# Utility functions
# -----------------------------

def get_datetime(href):
    start_datetime = assign_start_datetime(href)
    end_datetime = assign_end_datetime(href)
    if start_datetime:
        start_datetime = start_datetime.replace(tzinfo=timezone.utc)
    if end_datetime:
        end_datetime = end_datetime.replace(tzinfo=timezone.utc)
    return start_datetime, end_datetime

def get_thumbnail_asset(url):
    base_filename = os.path.basename(url)
    thumbnail_name = os.path.splitext(base_filename)[0] + ".png"
    thumbnail_url = f"{thumbnail_folder}/{thumbnail_name}"
    return {
        "href": thumbnail_url,
        "title": "Thumbnail",
        "type": "image/png",
        "roles": ["thumbnail"],
    }

# -----------------------------
# STAC item creation
# -----------------------------

def create_item(href):  
    start_datetime, end_datetime = get_datetime(href)
    asset_roles = ['data', 'visual']
    asset_media_type = "image/tiff; application=geotiff; profile=cloud-optimized"  # STAC-compliant
    properties = get_item_properties(href)

    try:
        # Create STAC item
        item = create_stac_item(
            source=href,
            properties=properties,
            input_datetime=start_datetime,
            collection='dem-phase3-backup',
            with_proj=True,
            with_raster=True,
            with_eo=False,
            asset_roles=asset_roles,
            asset_media_type=asset_media_type,
        )

        # Force STAC 1.0.0
        item.stac_version = "1.0.0"

        # Add temporal info
        if start_datetime:
            item.properties["start_datetime"] = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        if end_datetime:
            item.properties["end_datetime"] = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Add thumbnail
        thumbnail_info = get_thumbnail_asset(href)
        if thumbnail_info:
            item.add_asset(
                "thumbnail",
                pystac.Asset(
                    href=thumbnail_info["href"],
                    media_type=thumbnail_info["type"],
                    roles=thumbnail_info["roles"],
                    title=thumbnail_info["title"]
                )
            )

        # Clear links
        item.links.clear()

        # Serialize and force STAC 1.0.0 in JSON
        item_dict = item.to_dict()
        item_dict["stac_version"] = "1.0.0"

        # Write JSON
        outfile = os.path.join(output_dir, f"{item.id}.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(outfile, 'w') as f:
            json.dump(item_dict, f, indent=2)

        print(f"✅ STAC item created: {item.id}")
        return item

    except Exception as e:
        print(f"❌ Failed for {href}: {e}")
        return None

# -----------------------------
# Bulk processing
# -----------------------------

def process_bulk(urls, max_workers=48):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(create_item, url): url for url in urls}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"❌ Exception processing {futures[future]}: {e}")

# -----------------------------
# Main
# -----------------------------

if __name__ == '__main__':
    item_collection = "dem-phase3-backup"
    # thumbnail_folder = f"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/{item_collection}"
    thumbnail_folder =  r"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/dem-phase3"
    output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/{item_collection}" 

    # Load URLs from CSV
    CSV_PATH = r"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/dem-phase3.csv"
    urls_to_process = pd.read_csv(CSV_PATH)['aws_url'].dropna().tolist()

    if not urls_to_process:
        urls_to_process = ['https://kyfromabove.s3.us-west-2.amazonaws.com/elevation/DEM/Phase3/N075E399_2025_DEM_Phase3_cog.tif']

    # Run bulk processing
    process_bulk(urls_to_process, max_workers=20)