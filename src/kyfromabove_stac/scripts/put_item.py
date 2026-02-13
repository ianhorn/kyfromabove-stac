import json
import requests

def put_item(file, phase):
    api_url_base = f"https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/"

    # Load STAC Item from file
    with open(file, "r", encoding="utf-8") as f:
        item = json.load(f)

    item_id = item["id"]

    # Build full URL
    put_url = f"{api_url_base}{phase}/items/{item_id}"

    # Send PUT request
    response = requests.put(
        put_url,
        headers={"Content-Type": "application/json"},
        json=item
    )

    print(f"→ PUT {put_url}")
    if response.status_code in [200, 201]:
        print("✅ Item successfully updated.")
    else:
        print(f"❌ Failed to PUT item: {response.status_code}")
        print(response.text)

    return item

if __name__ == "__main__":
    file = r"C:\Users\Ian.Horn\Documents\stac-repos\kyfromabove-stac\items\dem-phase3-backup\N036E321_2025_DEM_Phase3_cog.tif.json"
    phase = "dem-phase3-backup"

    put_item(file, phase)