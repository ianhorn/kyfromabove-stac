"""
This python script creates a function that will be used to populate
stac-item variables.  

It will then use the titiler.extension to create a stac item

Based on stac.py from which basically is rio-stac Extension.
"""
import requests
import json
from constants_titiler import assign_datetime #, assign_collection

titiler_endpoint = "https://6hp4guqpwe.execute-api.us-west-2.amazonaws.com/cog/stac"

def get_item_attributes(url):
    datetime_str = assign_datetime(url) or "2025-03-05T00:00:00Z"

    # collection = assign_collection(url)
    
    return datetime_str  # , collection

def create_stac_item(url):
    datetime_str = get_item_attributes(url)
    
    params = {
        "url": url,
        "datetime": datetime_str,
        # "collection": collection,
        "asset_roles": "data",
        "with_eo": "false"
    }

    try:
        response = requests.get(titiler_endpoint, params=params)

        if response.ok:
            item = response.json()
            print(json.dumps(item, indent=2))
            return item
        else:
            print("Failed to process", url)
            print("Status code:", response.status_code)
            print("Response text:", response.text)
            return None

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
        return None

def main(url):
    create_stac_item(url)

if __name__ == "__main__":
    url = "https://kyfromabove.s3.us-west-2.amazonaws.com/elevation/DEM/Phase3/N038E327_2025_DEM_Phase3_cog.tif"
    main(url)