"""
This script leverages the titiler API running on a localhost host
to get coordinates that are then used to create thumbnails of the 
various items.
Files will be saved locally then loaded to AWS or directly save to AWS.
"""

import os
import gc
import pandas as pd
import requests
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed

# edit these three variable according to different collections
product = "dem-phase1"
image_service = "Ky_DEM_KYAPED_5FT"
category = "Image"

#thumbnail size:
size = "200,200"
# compression quality
cq = ""

output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/thumbnails/{product}"
image_service = "Ky_KYAPED_Phase2_6IN"
titiler_endpoint = "http://localhost:8000/cog/bounds"
csv = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{product}.csv"

os.makedirs(output_dir, exist_ok=True)
data = pd.read_csv(csv)

def get_thumbnail_url(url):
    try:
        response = requests.get(titiler_endpoint, params={"url": url})
        if response.ok:
            bounds = response.json().get("bounds", [])
            if not bounds:
                return None
            bbox = ",".join(map(str, bounds))
            return (
                f"https://kyraster.ky.gov/arcgis/rest/services/"
                f"{category}Services/{image_service}_WGS84WM/ImageServer/"
                f"exportImage?bbox={bbox}&bboxSR=4326&imageSR=3857&"
                f"format=pngjpg&compressionQuality={cq}&size={size}&f=image"
            )
        return None
    except Exception as e:
        print("Error getting bounds:", e)
        return None

def create_thumbnail(url):
    image_name = os.path.basename(url)
    thumbnail_url = get_thumbnail_url(url)
    if not thumbnail_url:
        return

    try:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "").lower()
            ext = mimetypes.guess_extension(content_type)
            # if ext is None:
            #     ext = ".jpg" if "jpeg" in content_type else ".png"
            ext = ".png"
            outfile = os.path.join(output_dir, os.path.splitext(image_name)[0] + ext)
            if os.path.exists(outfile):
                print(f"Skipping (already exists): {outfile}")
                return
            with open(outfile, "wb") as file:
                file.write(response.content)
            print(f"Thumbnail saved: {outfile}")
        else:
            print(f"Bad response: {response.status_code} for {url}")
    except Exception as e:
        print(f"Error downloading thumbnail for {url}:", e)
    finally:
        gc.collect()

if __name__ == "__main__":
    urls = data["aws_url"].dropna().tolist()

    # Use a thread pool with 10 workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_thumbnail, url) for url in urls]
        for future in as_completed(futures):
            # Optional: catch unexpected errors
            try:
                future.result()
            except Exception as e:
                print("Unhandled error:", e)