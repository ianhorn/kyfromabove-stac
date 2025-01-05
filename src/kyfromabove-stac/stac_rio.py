# import rio-stac because I like the final product
from rio_stac import create_stac_item
import json
import os
from datetime import datetime

from item_constants import (assign_start_datetime,
                            assign_end_datetime,
                            assign_collection) 



def get_eo(href):
    """
    if it's imagery return eo bands
    """
    if "orthos" in href:
        eo = True
    else:
        eo = False
    return eo
def get_datetime(href):
    """
    Returns the start and end datetime as datetime objects.
    """
    start_datetime = assign_start_datetime(href)
    end_datetime = assign_end_datetime(href)

    # Print for debugging
    print(f"Start datetime: {start_datetime}, End datetime: {end_datetime}")

    return start_datetime, end_datetime  # Return datetime objects directly

def create_item(href):  
    """
    Set the parameters I want
    """
    id = os.path.basename(href)  # Use only the filename as the ID
    collection = assign_collection(href)
    eo = get_eo(href)
    start_datetime, end_datetime = get_datetime(href)

    print(f"Creating STAC item with ID: {id}, Collection: {collection}, Source: {href}")

    try:
        # Create the STAC item
        item = create_stac_item(
            id=id,
            input_datetime=start_datetime,  # Required field for the datetime
            collection=collection,
            with_proj=True,
            with_raster=True,
            with_eo=eo,
            source=href
        )

        # Add temporal range to the item's properties if applicable
        if end_datetime:
            item.properties["start_datetime"] = start_datetime.isoformat()
            item.properties["end_datetime"] = end_datetime.isoformat()

        print("STAC item created successfully.")
        return item

    except Exception as e:
        print(f"Error creating STAC item: {e}")
        return None


def main(input_file, output_dir):
    href = input_file

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  

    item = create_item(href)  # Get the created item

    if item is None:
        print("Failed to create STAC item. Exiting.")
        return

    file_path = os.path.basename(href).replace(".tif", ".json")
    stac_json = os.path.join(output_dir, file_path)

    # Write the STAC item to a JSON file
    with open(stac_json, 'w') as f:
        json.dump(item.to_dict(), f, indent=4)  # Use `to_dict()` method to serialize
        print(f"Saved {stac_json} to file.")
if __name__ == '__main__':
    input_file = 'https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2023_Season1_3IN/N036E330_2023_Season1_3IN_cog.tif'
    output_dir = 'c:/users/ian.horn/downloads/temp/items'
    main(input_file, output_dir)
