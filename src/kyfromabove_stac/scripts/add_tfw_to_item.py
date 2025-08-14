import requests

API_URL = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com"
COLLECTIONS = ["orthos-phase1", "orthos-phase2"]
HEADERS = {"accept": "application/json", "Content-Type": "application/json"}

def get_all_items(collection):
    """Generator to yield all items from a collection."""
    next_url = f"{API_URL}/collections/{collection}/items?limit=100"
    while next_url:
        response = requests.get(next_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        for item in data["features"]:
            yield item
        next_url = data.get("links", [])
        next_url = next((link["href"] for link in next_url if link.get("rel") == "next"), None)

def add_worldfile_asset(item):
    """Add a .tfw world file asset based on the .tif COG asset."""
    assets = item.get("assets", {})
    cog_key = next((k for k, v in assets.items() if v["href"].endswith(".tif")), None)
    if not cog_key:
        return None  # skip if no .tif

    cog_href = assets[cog_key]["href"]
    tfw_href = cog_href.replace(".tif", ".tfw")

    if "metadata" in assets:
        return None  # already has metadata

    assets["metadata"] = {
        "href": tfw_href,
        "type": "text/plain",
        "roles": ["metadata"],
        "title": "world file"
    }
    item["assets"] = assets
    return item

def put_item_back(item, collection):
    """PUT the updated item back to the STAC API."""
    item_id = item["id"]
    url = f"{API_URL}/collections/{collection}/items/{item_id}"
    response = requests.put(url, headers=HEADERS, json=item)

    if response.status_code == 200:
        print(f"✅ Updated: {item_id}")
    else:
        print(f"❌ Failed to update {item_id} ({response.status_code})")
        print(response.text)

def process_collection(collection):
    print(f"\n📦 Processing collection: {collection}")
    count_updated = 0
    for item in get_all_items(collection):
        updated_item = add_worldfile_asset(item)
        if updated_item:
            put_item_back(updated_item, collection)
            count_updated += 1
    print(f"✅ Finished {collection}: {count_updated} items updated.")

if __name__ == "__main__":
    for collection in COLLECTIONS:
        process_collection(collection)