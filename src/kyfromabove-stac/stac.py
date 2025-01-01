from pystac import Item, Asset
from pystac.extensions.projection import ProjectionExtension
import os
import rasterio
from rasterio.warp import transform_bounds
import json
from item_constants import (
    get_item_properties,
    assign_start_datetime,
    assign_end_datetime,
    assign_collection
)

def create_stac_item(href):
    """
    Get raster info to populate extensions and create a STAC item
    """
    with rasterio.open(href) as r:
        # Transform bounds to WGS84
        bbox_wgs84 = transform_bounds(r.crs, "EPSG:4326", *r.bounds, densify_pts=21)
        bbox_proj = list(r.bounds)
        geometry_proj = {
            "type": "Polygon",
            "coordinates": [[
                [r.bounds.left, r.bounds.bottom],
                [r.bounds.left, r.bounds.top],
                [r.bounds.right, r.bounds.top],
                [r.bounds.right, r.bounds.bottom],
                [r.bounds.left, r.bounds.bottom]
            ]]
        }
        geometry_wgs84 = {
            "type": "Polygon",
            "coordinates": [[
                [bbox_wgs84[0], bbox_wgs84[1]],
                [bbox_wgs84[0], bbox_wgs84[3]],
                [bbox_wgs84[2], bbox_wgs84[3]],
                [bbox_wgs84[2], bbox_wgs84[1]],
                [bbox_wgs84[0], bbox_wgs84[1]]
            ]]
        }

        # Get raster band information
        bands = [
            {"band": i + 1, "type": str(r.dtypes[i]), "description": f"Band {i + 1}"}
            for i in range(r.count)
        ]

        # Generate STAC item
        id = os.path.basename(href)
        collection = assign_collection(href)
        start_datetime = assign_start_datetime(href)
        end_datetime = assign_end_datetime(href)
        properties = get_item_properties(href)
        extensions = ["https://stac-extensions.github.io/projection/v1.1.0/schema.json"]

        item = Item(
            id=id,
            datetime=start_datetime,
            properties=properties,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            collection=collection,
            geometry=geometry_wgs84,
            bbox=bbox_wgs84
        )
        if collection:
            item.collection = collection

        # Add projection extension
        ProjectionExtension.add_to(item)
        proj_ext = ProjectionExtension.ext(item)
        proj_ext.epsg = r.crs.to_epsg()
        proj_ext.geometry = geometry_proj
        proj_ext.bbox = bbox_proj
        proj_ext.shape = [r.height, r.width]
        proj_ext.transform = list(r.transform)

        # Define asset URL (assuming `href` as URL for the asset)
        asset_url = href

        # if "orthos" in asset_url:
        #     eo_bands = {
        #     "band 1": "red",
        #     "band 2": "green",
        #     "band 3": "red",
        #     "band 4": "nir"
        # }
        # else:
        #     return None

        # Define asset dictionary
        asset = Asset(
            href=asset_url,
            media_type="image/tiff; application=geotiff; profile=cloud-optimized",
            roles=["data"],
            title="asset",
            # extra_fields={"eo:bands": eo_bands if eo_bands else []}
        )
        
       
        # Add asset to item
        item.assets["asset"] = asset

                # Add extensions to item
        item.properties["extensions"] = extensions

        return item

def main(input_file, out_dir):
    """
    Input file can be a file locally or a s3 URL of a cloud-optimized format.
    """
    href = input_file

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Get the file name from href and remove the ".tif" extension
    file_path = os.path.basename(href).replace(".tif", "")
    item = create_stac_item(href)  # Create STAC item using href

    # Output the STAC item to a JSON file
    stac_json = os.path.join(out_dir, f"{file_path}.json")

    with open(stac_json, "w") as f:
        json.dump(item.to_dict(), f, indent=4)  # Save the item to a JSON file
        print(f"Saved {stac_json} to file.")

if __name__ == "__main__":
    input_file = "https://kyfromabove.s3.us-west-2.amazonaws.com/elevation/DEM/Phase1/N026E311_2012_DEM_Phase1_cog.tif"
    out_dir = "./items"
    main(input_file, out_dir)