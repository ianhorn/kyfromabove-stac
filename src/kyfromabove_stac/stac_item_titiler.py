"""
This python script creates a function that will be used to populate
stac-item variables.

It will then use the titiler.extension to create a stac item

Based on stac.py from which basically is rio-stac Extension.
"""

import os
import json
import requests
import pystac

from constants_titiler import assign_datetime, assign_collection

titiler_endpoint = "http://localhost:8000/cog/stac"
item_collection = "orthos-phase3"
stac_api_url = f"https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/{item_collection}/items"
thumbnail_folder = f"https://kyfromabove-stac-us-west-2.s3.us-west-2.amazonaws.com/items/thumbnails/{item_collection}"
item_output = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items_v1.1.0/{item_collection}"

def get_tfw_asset(url):
  world_file = os.path.splitext(url)[0] + ".tfw"
  
  return {
    "href": world_file,
    "title": "World File",
    "type": "text/plain",
    "roles": ["metadata"]
  }

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

def get_item_attributes(url):
  """Calling attributes from constants_titiler.py"""
  datetime_str = assign_datetime(url)
  collection = assign_collection(url)
  return datetime_str, collection

def create_stac_item(url):
  datetime_str, collection = get_item_attributes(url)

  params = {
    "url": url,
    "datetime": datetime_str,
    "collection": collection,
    "asset_media_type": "image/tiff; application=geotiff; profile=cloud-optimized",
    "asset_roles": ["data", "visual"],
  }

  try:
    response = requests.get(titiler_endpoint, params=params)
    if response.ok:
      item = response.json()

      # Add thumbnail asset
      thumbnail_asset = get_thumbnail_asset(url)
      tfw_asset = get_tfw_asset(url)
      if "assets" not in item or not isinstance(item["assets"], dict):
        item["assets"] = {}
      item["assets"]["thumbnail"] = thumbnail_asset
      item["assets"]["metadata"] = tfw_asset    
      item["properties"].pop("datetime", None) 
  

      print(json.dumps(item, indent=2))

      # Validate STAC item
      try:
        stac_item = pystac.Item.from_dict(item)
        stac_item.validate()
        print("✅ STAC item validated successfully.")
      except Exception as e:
        print(f"❌ STAC item validation failed: {e}")
        return None

      # ✅ Post to STAC API
      try:
          post_response = requests.post(
              stac_api_url,
              headers={"Content-Type": "application/json"},
              data=json.dumps(item)
          )
          if post_response.ok:
              print("✅ STAC item posted successfully.")
          else:
              print("❌ Failed to post STAC item.")
              print("Status code:", post_response.status_code)
              print("Response:", post_response.text)
      except Exception as e:
          print("❌ Error posting to STAC API:", e)

      # ✅ Write to disk
      try:
        base_filename = os.path.basename(url)
        item_name = os.path.splitext(base_filename)[0] + ".json"
        output_path = f"{item_output}/{item_name}"

        # Make sure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
          json.dump(item, f, indent=2)
        print(f"✅  item written to {output_path}")
      except Exception as e:
        print("❌ Error writing STAC item to disk:", e)

      return item

    else:
      print("❌ Failed to process", url)
      print("Status code:", response.status_code)
      print("Response text:", response.text)
      return None

  except Exception as e:
    print(f"❌ Error occurred while processing {url}: {e}")
    return None

def main(url):
  create_stac_item(url)

if __name__ == "__main__":
  url = "https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2024_Season1_3IN/N203E093_2024_Season1_3IN_cog.tif"
  main(url)