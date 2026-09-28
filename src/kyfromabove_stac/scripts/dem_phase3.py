import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CSV_FILE = Path(r"C:\Users\Ian.Horn\Documents\stac-repos\kyfromabove-stac\csv\dem-phase3.csv")
OUTPUT_DIR = Path(r"C:\Users\Ian.Horn\Documents\stac-repos\kyfromabove-stac\items\dem-phase3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TITILER_ENDPOINT = ("https://6hp4guqpwe.execute-api.us-west-2.amazonaws.com/cog/stac")
THUMBNAIL_BASE = (
    "https://kyfromabove-stac.s3.us-west-2.amazonaws.com/"
    "collections/dem-phase3/thumbnails"
)
HARDCODED_DATETIME = "2026-02-13T00:00:00Z"
HARDCODED_END_DATETIME = "2026-03-12T00:00:00Z"

MAX_WORKERS = 28


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def worldfile_url(raster_url: str) -> str:
    """Return the .tfw URL corresponding to a .tif URL."""
    return f"{raster_url.rsplit('.', 1)[0]}.tfw"


def create_stac_item(url: str):
    """Create a STAC item using TiTiler's STAC response as the source."""

    try:
        # -------------------------------------------------------------------
        # Get STAC metadata from TiTiler
        # -------------------------------------------------------------------

        response = requests.get(
            TITILER_ENDPOINT,
            params={
                "url": url,
                "with_eo": "false",
                "asset_roles": "data",
            },
            timeout=60,
        )

        response.raise_for_status()

        tiler_item = response.json()

        # -------------------------------------------------------------------
        # Use the filename without .tif as the STAC item ID
        # -------------------------------------------------------------------

        filename = url.rsplit("/", 1)[-1]
        item_id = filename.rsplit(".", 1)[0]

        # -------------------------------------------------------------------
        # Preserve TiTiler's properties exactly.
        #
        # This is important because TiTiler provides:
        #
        #   proj:projjson
        #   proj:shape
        #   proj:transform
        #   proj:bbox
        #   proj:geometry
        #
        # including the compound CRS:
        #
        # NAD83 / Kentucky Single Zone (ftUS)
        # + NAVD88 height (ftUS)
        # -------------------------------------------------------------------

        properties = tiler_item.get("properties", {}).copy()

        # Add/update the dates used by the KyFromAbove collection.
        properties["start_datetime"] = HARDCODED_DATETIME
        properties["end_datetime"] = HARDCODED_END_DATETIME
        properties["datetime"] = HARDCODED_DATETIME

        # Add the collection license.
        properties["license"] = "CC-BY-4.0"

        # -------------------------------------------------------------------
        # Get the data asset returned by TiTiler.
        #
        # This contains raster:bands, including:
        #   data_type
        #   nodata
        #   unit
        #   statistics
        #   histogram
        # -------------------------------------------------------------------

        tiler_data_asset = tiler_item.get("assets", {}).get("data", {})

        data_asset = tiler_data_asset.copy()

        # Keep the actual COG URL and identify it as data/visual.
        data_asset["href"] = url
        data_asset["type"] = (
            "image/tiff; application=geotiff; profile=cloud-optimized"
        )
        data_asset["roles"] = ["data", "visual"]

        # -------------------------------------------------------------------
        # Thumbnail
        # -------------------------------------------------------------------

        thumbnail_url = (
            f"{THUMBNAIL_BASE}/{Path(filename).stem}.png"
        )

        thumbnail_asset = {
            "href": thumbnail_url,
            "type": "image/png",
            "roles": ["thumbnail"],
            "title": "Thumbnail image",
        }

        # -------------------------------------------------------------------
        # World file
        # -------------------------------------------------------------------

        worldfile_asset = {
            "href": worldfile_url(url),
            "type": "text/plain",
            "roles": ["metadata", "worldfile"],
            "title": "World file",
        }

        # -------------------------------------------------------------------
        # Build final STAC item.
        #
        # Projection and raster metadata come directly from TiTiler.
        # -------------------------------------------------------------------

        item = {
            "type": tiler_item.get("type", "Feature"),
            "stac_version": tiler_item.get("stac_version", "1.1.0"),
            "stac_extensions": tiler_item.get("stac_extensions", []),
            "id": item_id,
            "geometry": tiler_item["geometry"],
            "bbox": tiler_item["bbox"],
            "properties": properties,
            "links": [],
            "assets": {
                "data": data_asset,
                "thumbnail": thumbnail_asset,
                "worldfile": worldfile_asset,
            },
        }

        # -------------------------------------------------------------------
        # Write item
        # -------------------------------------------------------------------

        output_file = OUTPUT_DIR / f"{item_id}.json"

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(item, f, indent=2)

        return output_file, None

    except Exception as e:
        return None, f"{url}: {e}"


# ---------------------------------------------------------------------------
# Read CSV
# ---------------------------------------------------------------------------

df = pd.read_csv(CSV_FILE)

# Assumes the CSV contains a column named "url".
urls = df["url"].dropna().astype(str).tolist()

print(f"Found {len(urls):,} DEM URLs")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Using {MAX_WORKERS} workers")
print()


# ---------------------------------------------------------------------------
# Process concurrently
# ---------------------------------------------------------------------------

completed = 0
failed = 0

lock = Lock()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

    futures = {
        executor.submit(create_stac_item, url): url
        for url in urls
    }

    for future in as_completed(futures):

        output_file, error = future.result()

        with lock:
            if error:
                failed += 1
                print(f"ERROR: {error}")
            else:
                completed += 1
                print(
                    f"[{completed + failed:,}/{len(urls):,}] "
                    f"Wrote {output_file.name}"
                )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print()
print("Complete")
print(f"  Successful: {completed:,}")
print(f"  Failed:     {failed:,}")
print(f"  Total:      {len(urls):,}")