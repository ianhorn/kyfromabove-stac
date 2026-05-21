#!/usr/bin/env python

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

product = "dem-phase3"
image_service = "Ky_DEM_KYAPED_2FT_Phase3"
category = "Elevation"

titiler_endpoint = "https://6hp4guqpwe.execute-api.us-west-2.amazonaws.com/cog/bounds"

csv = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/{product}.csv"

output_dir = (
    f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/thumbnails/{product}"
)

os.makedirs(output_dir, exist_ok=True)

data = pd.read_csv(csv)

session = requests.Session()


def get_thumbnail_url(url):

    print(f"Getting bounds for: {url}")

    try:
        response = session.get(
            titiler_endpoint,
            params={"url": url},
            timeout=30,
        )

        print(f"Titiler status: {response.status_code}")

        response.raise_for_status()

        bounds = response.json().get("bounds")

        if not bounds:
            print("No bounds returned")
            return None

        bbox = ",".join(map(str, bounds))

        print(f"BBox: {bbox}")

        if category == "Elevation":

            rendering_rule = json.dumps(
                {
                    "rasterFunction": "Hillshade",
                    "rasterFunctionArguments": {
                        "HillshadeType": 1,
                        "ZFactor": 1,
                    },
                    "variableName": "DEM",
                }
            )

            thumbnail_url = (
                "https://kyraster.ky.gov/arcgis/rest/services/ElevationServices/"
                "Ky_DSM_First_Return_5FT_Phase1/ImageServer/exportImage"
                f"?bbox={bbox}&bboxSR=4326&size=200,200&imageSR=3089"
                "&format=png&pixelType=UKNOWN&interpolation=RSP_BilinearInterpolation"
                f"&renderingRule={rendering_rule}&f=image"
            )

            print(thumbnail_url)

            return thumbnail_url

        elif category == "Image":

            return (
                "https://kyraster.ky.gov/arcgis/rest/services/"
                f"ImageServices/{image_service}_WGS84WM/"
                "ImageServer/exportImage"
                f"?bbox={bbox}"
                "&bboxSR=4326"
                "&size=200,200"
                "&format=png"
                "&interpolation=RSP_BilinearInterpolation"
                "&f=image"
            )

    except Exception as e:
        print(f"Error getting bounds: {e}")
        return None


def create_thumbnail(url):

    image_name = os.path.basename(url)

    outfile = os.path.join(
        output_dir,
        os.path.splitext(image_name)[0] + ".png",
    )

    if os.path.exists(outfile):
        print(f"Skipping existing: {outfile}")
        return

    thumbnail_url = get_thumbnail_url(url)

    if not thumbnail_url:
        return

    try:

        print("Downloading thumbnail...")

        response = session.get(
            thumbnail_url,
            timeout=60,
        )

        print(f"Thumbnail response: {response.status_code}")

        response.raise_for_status()

        with open(outfile, "wb") as file:
            file.write(response.content)

        print(f"Saved: {outfile}")

    except Exception as e:
        print(f"Error creating thumbnail: {e}")


if __name__ == "__main__":

    urls = data["aws_url"].dropna().tolist()

    print(f"Found {len(urls)} URLs")

    with ThreadPoolExecutor(max_workers=20) as executor:

        futures = [
            executor.submit(create_thumbnail, url)
            for url in urls
        ]

        for future in as_completed(futures):

            try:
                future.result()

            except Exception as e:
                print(f"Unhandled worker error: {e}")