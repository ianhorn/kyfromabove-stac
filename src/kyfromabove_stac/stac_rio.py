# import rio-stac because I like the final product
from rio_stac import create_stac_item
from datetime import timezone
import os
import pystac
import json

from item_constants import (assign_start_datetime,
                            assign_end_datetime,
                            assign_collection,
                            get_item_properties) 

def get_datetime(href):
    """
    Returns the start and end datetime as datetime objects.
    """
    start_datetime = assign_start_datetime(href)
    end_datetime = assign_end_datetime(href)

    # Make the datetime objects timezone-aware (UTC)
    start_datetime = start_datetime.replace(tzinfo=timezone.utc)  # Set UTC timezone
    end_datetime = end_datetime.replace(tzinfo=timezone.utc)      # Set UTC timezone

    # Print for debugging
    # print(f"\nStart datetime: {start_datetime}, End datetime: {end_datetime}\n")

    return start_datetime, end_datetime  # Return datetime objects directly

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


def create_item(href):  
    """
    Set the parameters I want
    """
    collection = assign_collection(href)
    start_datetime, end_datetime = get_datetime(href)  # pulls the datetime from the name in the constants script
    asset_roles = ['data', 'visual', ]  # have to set this up as a dictionary or it won't validate
    asset_media_type = "image/tiff; application=geotiff; profile=cloud-optimized",
    properties = {}
    properties = get_item_properties(href)
    if "cog" in href.lower():
        asset_media_type = "image/tiff; application=geotiff; cloud-optimized"

    # print(f"Creating STAC item with ID: {id}, Collection: {collection}, Source: {href}\n")

    try:
        # Create the STAC item
        item = create_stac_item(
            source=href,
            # id=id  # rio-stac pulls from source
            properties = properties,
            input_datetime=start_datetime,  # Required field for the datetime
            collection=collection,
            with_proj=True,
            with_raster=True,
            with_eo = False,  # not relevant to KyFromAbove data, collection is standardized
            asset_roles=asset_roles,
            asset_media_type = asset_media_type,
        )

        # Add temporal range to the item's properties if applicable
        if end_datetime:
            item.properties["start_datetime"] = start_datetime.strftime('%Y-%m-%dT%H:%M:%S') + "Z"  # With UTC offset
            item.properties["end_datetime"] = end_datetime.strftime('%Y-%m-%dT%H:%M:%S') + "Z"  # With UTC offset

        print(f"STAC item {item.id} created successfully.")

        # Add thumbnail asset
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
            print(f"Thumbnail added for {item.id}")
            
        print(json.dumps(item.to_dict(), indent=2))
        
        outfile = os.path.join(output_dir, f"{item.id}.json")
        
        
        with open(outfile, 'w') as f:
            json.dump(item.to_dict(), f, indent=2)
        print(f"✅  item written to {outfile}")

        return item
    
    except Exception as e:
        print(e)


# def main(input_file, output_dir):
def main(input_file):
    href = input_file

    item = create_item(href)  # Get the created item

    if item is None:
        print("Failed to create STAC item. Exiting.\n")
        return
    # else:
    #     print(json.dumps(item.to_dict(), indent=2))
if __name__ == '__main__':
    input_file = 'https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2024_Season1_3IN/N203E093_2024_Season1_3IN_cog.tif'
    # titiler_endpoint = "http://localhost:8000/cog/stac"
    item_collection = "orthos-phase3"
    # stac_api_url = f"https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/{item_collection}/items"
    thumbnail_folder = f"https://kyfromabove-stac-us-west-2.s3.us-west-2.amazonaws.com/items/thumbnails/{item_collection}"
    output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items_v1.1.0/{item_collection}" 
    
    main(input_file)