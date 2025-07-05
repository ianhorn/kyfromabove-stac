import json
import requests

def put_item(file, phase):
    api_url_base = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/"

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
    file = "C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/dems/N201E070_2020_DEM_Phase2_cog.json"
    phase = "dem-phase2"

    put_item(file, phase)