import requests
import os
import json

# Configuration
collection_id = "dem-phase2"
base_url = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com"
output_dir = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/{collection_id}"
os.makedirs(output_dir, exist_ok=True)

def save_item(item):
    item_id = item["id"]
    filename = os.path.join(output_dir, f"{item_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)
    print(f"✅ Saved: {filename}")

def fetch_items(collection_id):
    url = f"{base_url}/collections/{collection_id}/items"
    params = {
        "limit": 100  # Adjust depending on your API's max page size
    }

    while url:
        print(f"🔄 Fetching: {url}")
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ Failed to fetch items: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        for item in data.get("features", []):
            save_item(item)

        # Get next page if it exists
        links = data.get("links", [])
        next_link = next((l["href"] for l in links if l.get("rel") == "next"), None)
        url = next_link
        params = None  # After first page, next URL already contains all params

if __name__ == "__main__":
    fetch_items(collection_id)
    print("🎉 Done downloading items.")