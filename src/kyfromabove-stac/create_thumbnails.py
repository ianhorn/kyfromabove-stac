"""
This script leverages the titiler API running on a localhost host
to get coordinates that are then used to create thumbnails of the 
various items.

Files will be saved locally then loaded to AWS or directly save to AWS.
"""

import requests
import json
import os
import pandas as pd
import multiprocessing
import gc

product = "dem-phase3"
output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/collections/thumbnails/{product}"
image_service = "Ky_DEM_KYAPED_2FT_Phase3"
category = "Elevation"
titiler_endpoint = "http://localhost:8000/cog/bounds"  # fixed endpoint
csv = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{product}.csv"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

data = pd.read_csv(csv)

def get_thumbnail_url(url):
    try:
        response = requests.get(titiler_endpoint, params={"url": url})
        if response.ok:
            data = response.json()
            bounds = data.get("bounds", [])
            if not bounds:
                print("No bounds returned for", url)
                return None
            bbox = ",".join(map(str, bounds))

            thumbnail_url = (
                f"https://kyraster.ky.gov/arcgis/rest/services/"
                f"{category}Services/{image_service}_WGS84WM/ImageServer/"
                f"exportImage?bbox={bbox}&bboxSR=4326&imageSR=3857&format=png&size=431,350&f=image"
            )

            return thumbnail_url
        else:
            print("Failed to process", url)
            return None

    except Exception as e:
        print("Error in get_thumbnail_url:", e)
        return None
        
def create_thumbnail(url):
    image_name = os.path.basename(url)
    outfile = os.path.join(output_dir, os.path.splitext(image_name)[0] + ".png")
    
        # Skip if file already exists
    if os.path.exists(outfile):
        print(f"Skipping (already exists): {outfile}")
        return
    
    thumbnail_url = get_thumbnail_url(url)
    if not thumbnail_url:
        return

    try:
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            with open(outfile, "wb") as file:
                file.write(response.content)
            print(f"Thumbnail saved: {outfile}")
        else:
            print(f"Failed to retrieve thumbnail: HTTP {response.status_code}")
            
    except Exception as e:
        print("Error downloading thumbnail:", e)
        
    gc.collect()

if __name__ == "__main__":
    with multiprocessing.Pool(processes=18) as pool:
        pool.map(create_thumbnail, data["aws_url"])