"""
Test out on indivual tiles
"""

from pystac import Item
import os
from item_constants_test import (
    get_bbox_and_footprint,
    get_item_properties,
    get_stac_extensions,
    assign_start_datetime,
    assign_end_datetime,
    assign_collection
)
import pandas as pd
import json

def create_stac_item(href):

    id = os.path.basename(href).replace(".tif", "")
    bbox, footprint, crs = get_bbox_and_footprint(href)
    collection = assign_collection(href)
    start_datetime = assign_start_datetime(href)
    end_datetime = assign_end_datetime(href)
    properties = get_item_properties(href)
    extensions = get_stac_extensions(href)

    item = Item(
        id=id,
        geometry=footprint,
        bbox=bbox,
        crs=crs,
        datetime=None,
        properties=properties,
        collection=collection,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        extensions=extensions
    )

    return item

def main(input_list, out_dir, column_name):

    data = pd.read_csv(input_list)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for __, row in data.iterrow():
        href = row[column_name]
        file_path = os.path.basename(row).replace(".tif", "")
        item = create_stac_item(row)

        stac_json = os.path.join(out_dir, f"file_path".json)

        with open(item.to_dict(), "w"):
            json.dump(item, stac_json, indent="4")
            print(f"Saved {stac_json} to file.")

if __name__ == "__main__":
    input_list = "C:/users/ian.horn/documents/stac-repos/kyfromabove-stac/csv/phase3_orthos.csv"
    out_dir = "C:/users/ian.horn/documents/stac-repos/kyfromabove-stac/tests/items"
    column_name = "url"
    main(input_list, out_dir, column_name)