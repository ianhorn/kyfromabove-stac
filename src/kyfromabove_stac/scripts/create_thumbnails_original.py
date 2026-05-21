"""
This script leverages the titiler API running on a localhost host
to get coordinates that are then used to create thumbnails of the 
various items.
Files will be saved locally then loaded to AWS or directly save to AWS.
"""
"""
This script leverages the titiler API running on localhost
to get bounding boxes that are used to create thumbnails of
various items. Files will be saved locally and optionally uploaded to AWS.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

# Editable parameters
product = "orthos-phase3"
image_service = "Ky_KYAPED_Phase3_3IN"
category = "Image"
size = "200,200"
cq = ""  # compression quality, if applicable
titiler_endpoint = "http://localhost:8000/cog/bounds"

csv = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{product}.csv"
output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/thumbnails/{product}"
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
            print(f"BBox: {bbox}")

            if category == "Elevation":
                return (
                    f"https://kyraster.ky.gov/arcgis/rest/services/ElevationServices/"
                    f"{image_service}_WGS84WM/ImageServer/exportImage?bbox={bbox}&bboxSR=4326&"
                    f"size=200%2C200&imageSR=&time=&format=png&pixelType=F32&noData=&"
                    f"noDataInterpretation=esriNoDataMatchAny&interpolation=+RSP_BilinearInterpolation&"
                    f"compression=&compressionQuality=&bandIds=&mosaicRule=&renderingRule=&f=image"
                )
            elif category == "Image":
                return (
                    f"https://kyraster.ky.gov/arcgis/rest/services/ImageServices/"
                    f"{image_service}_WGS84WM/ImageServer/exportImage?bbox={bbox}"
                    f"&bboxSR=4326&size=200%2C200&imageSR=&time=&format=png&pixelType="
                    f"U8&noData=&noDataInterpretation=esriNoDataMatchAny&"
                    f"interpolation=+RSP_BilinearInterpolation&compression="
                    f"compressionQuality=75&bandIds=&mosaicRule=&renderingRule=&f=image"
                )
            else: 
                print("something is wrong with your image service URL\n")
        else:
            print(f"Titiler bounds request failed: {response.status_code}")
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
            ext = ".png"  # force PNG because ArcGIS usually responds with it
            outfile = os.path.join(output_dir, os.path.splitext(image_name)[0] + ext)
            if os.path.exists(outfile):
                print(f"Skipping (already exists): {outfile}")
                return
            with open(outfile, "wb") as file:
                file.write(response.content)
            print(f"Thumbnail saved: {outfile}")
        else:
            print(f"Bad response ({response.status_code}) for {thumbnail_url}")
    except Exception as e:
        print("Error creating thumbnail:", e)

if __name__ == "__main__":
    urls = data["aws_url"].dropna().tolist()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_thumbnail, url) for url in urls]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("Unhandled error in worker:", e)