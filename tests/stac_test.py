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
import rasterio
import pandas as pd
import json

def create_stac_item(href):

    id = os.path.basename(href)
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
        datetime=None,
        properties=properties,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )
    if collection:
        item.collection = collection

    item.properties["extensions"] = extensions
        # Apply projection and raster extensions
    item.stac_extensions.append("projection")  # Add projection extension
    item.properties["proj:epsg"] = crs.to_epsg()  # Assuming crs is from rasterio and is a CRS object
    
        # Add raster extension properties
    item.stac_extensions.append("raster")
    with rasterio.open(href) as r:
        bands = [{"band": i+1, "type": "int16", "description": f"Band {i+1}"} for i in range(r.count)]
        item.properties["raster:bands"] = bands
        item.properties["raster:width"] = r.width
        item.properties["raster:height"] = r.height

    return item

def main(input_list, out_dir, column_name):
    if input_list is None:
        inputs = []
    
    data = pd.read_csv(input_list)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for __, row in data.iterrows():
        href = row[column_name]  # Access the href value (URL or file path) from the column
        file_path = os.path.basename(href).replace(".tif", "")  # Use the href to get the file name
        item = create_stac_item(href)  # Pass href, not the entire row

        stac_json = os.path.join(out_dir, f"{file_path}.json")  # Correct output filename

        with open(stac_json, "w") as f:
            json.dump(item.to_dict(), f, indent=4)  # Save the item to the JSON file
            print(f"Saved {stac_json} to file.")

if __name__ == "__main__":
    input_list = "C:/users/ian.horn/documents/stac-repos/kyfromabove-stac/csv/phase3_orthos.csv"
    out_dir = "C:/users/ian.horn/documents/stac-repos/kyfromabove-stac/tests/items"
    column_name = "url"  # Column in the CSV containing the file paths or URLs
    main(input_list, out_dir, column_name)