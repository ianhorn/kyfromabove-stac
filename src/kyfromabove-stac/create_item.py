import requests
import json
import pystac
from constants_titiler import assign_datetime, assign_collection

cogbounds_request_url = "http://localhost:8000/cog/bounds?url="
stac_request_url = "http://localhost:8000/cog/stac"
collection_id = "orthos-phase1"
stac_api_url = f"https://6xpdwhema7.execute-api.us-west-2.amazonaws.com/stac/collections/{collection_id}/items"

def create_thumbnail(url):
    try:
        response = requests.get(cogbounds_request_url, params={"url": url})
        if response.ok:
            data = response.json()
            bounds = data.get("bounds", [])
            bbox = ",".join(map(str, bounds))
            crs = data.get("crs", "")
            thumbnail_url = (
                f"https://kyraster.ky.gov/arcgis/rest/services/ImageServices/Ky_KYAPED_Phase2_6IN_WGS84WM/ImageServer/"
                f"exportImage?bbox={bbox}&bboxSR=4326&imageSR=3857&format=png&size=431,350&f=image"
            )

            thumbnail_asset = {
                "href": thumbnail_url,  # fixed
                "title": "Thumbnail",
                "type": "image/png",    # STAC-compliant key
                "roles": ["thumbnail"], # STAC-compliant key
            }

            return thumbnail_asset  # fixed
        else:
            print("Failed to process", url)
            return None

    except Exception as e:
        print("Error in create_thumbnail:", e)
        return None

def get_item_attributes(url):
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
        response = requests.get(stac_request_url, params=params)
        if response.ok:
            item = response.json()
            collection_id = item["collection"]

            # Add thumbnail asset
            thumbnail_asset = create_thumbnail(url)
            if thumbnail_asset:
                if "assets" not in item or not isinstance(item["assets"], dict):
                    item["assets"] = {}
                item["assets"]["thumbnail"] = thumbnail_asset

            # ✅ Validate with pystac
            try:
                import pystac
                stac_item = pystac.Item.from_dict(item)
                stac_item.validate()
                print("✅ STAC item validated successfully.")
            except Exception as e:
                print("❌ STAC validation failed:", e)
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
                output_path = "stac_item.json"
                with open(output_path, "w") as f:
                    json.dump(item, f, indent=2)
                print(f"✅  item written to {output_path}")
            except Exception as e:
                print("❌ Error writing STAC item to disk:", e)

            return item

        else:
            print("❌ Failed to create STAC item for", url)
            print("Status code:", response.status_code)
            print("Response text:", response.text)
            return None

    except Exception as e:
        print(f"❌ Error occurred while creating STAC item for {url}: {e}")
        return None

def main(url):
    create_stac_item(url)

if __name__ == "__main__":
    url = "https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase1/KY_KYAPED_2014_6IN/N135E128_2014_6IN_cog.tif"
    main(url)