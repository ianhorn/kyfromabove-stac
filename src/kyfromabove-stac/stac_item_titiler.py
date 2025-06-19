"""
This python script creates a function that will be used to populate
stac-item variables.  

It will then use the titiler.extension to create a stac item

Based on stac.py from which basically is rio-stac Extension.
"""


from system import os
import titiler 
from titiler.extensions import stac
from contants_titiler import assign_datetime, assign_collection
# datetime = assign_datetime(href)
# collection_id = assign_collection(href)
asset_roles = "data"

# def create_stac_item(href, dateteim, collection_id, asset_roles):
#     try:
#         item = stac.item(
#             url = href,
#             datetime = assign_datetime(href),
#             collection = assign_collection(href),
#             asset_roles = "data",
#             with_proj = True,
#             with_raster = True,
#             with_eo = False
#         )

#         return item

#     except Exception as e:
#         print(e)



def main(input_file, output_dir):
    href = input_file

    item = create_stac_item(href)  # Get the created item
    output_dir = output_dir

    if item is None:
        print("Failed to create STAC item. Exiting.\n")
        return
    else:
        print(json.dumps(item.to_dict(), indent=2))

if __name__ == '__main__':
    input_file = 'https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase3/KY_KYAPED_2023_Season1_3IN/N036E330_2023_Season1_3IN_cog.tif'
    output_dir = r'C:\Users\Ian.Horn\Documents\stac-repos\kyfromabove-stac\titiler-items'
    main(input_file)

