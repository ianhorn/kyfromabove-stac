# import rio-stac because I like the final product
from rio_stac import create_stac_item
from datetime import timezone

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

def create_item(href):  
    """
    Set the parameters I want
    """
    collection = assign_collection(href)
    start_datetime, end_datetime = get_datetime(href)  # pulls the datetime from the name in the constants script
    asset_roles = ['data']  # have to set this up as a dictionary or it won't validate
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
        return item

    except Exception as e:
        print(f"Error creating STAC item: {e}\n")
        return None


def main(input_file):
    href = input_file

    item = create_item(href)  # Get the created item

    if item is None:
        print("Failed to create STAC item. Exiting.\n")
        return
    # else:
    #     print(json.dumps(item.to_dict(), indent=2))
if __name__ == '__main__':
    input_file = 'https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2023_Season1_3IN/N036E330_2023_Season1_3IN_cog.tif'
    main(input_file)