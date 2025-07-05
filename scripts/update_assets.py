import os
import json

phase = "Phase2"
product = "dem-phase2"
stac_folder = "C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/dems"
thumbnail_base_url = f"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/items/thumbnails/{product}"

count = 0

for filename in os.listdir(stac_folder):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(stac_folder, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            print(f"⚠️ Skipping empty file: {filename}")
            continue
        try:
            item = json.loads(content)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON: {filename}")
            continue

    # Only process items that match the phase
    if phase not in item.get("id", ""):
        continue

    base_id = os.path.splitext(item["id"])[0]
    thumbnail_href = f"{thumbnail_base_url}/{base_id}.png"

    # Update COG asset media type
    for key, asset in item.get("assets", {}).items():
        href = asset.get("href", "")
        if href.endswith(".tif") or "cog" in key.lower():
            asset["type"] = "image/tiff; application=geotiff; profile=cloud-optimized"
            asset["roles"] = ["data", "visual"]

    # Add thumbnail asset
    item["assets"]["thumbnail"] = {
        "href": thumbnail_href,
        "type": "image/png",
        "roles": ["thumbnail"],
        "title": "Thumbnail image"
    }

    # Save updated item
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)
        print(f"✅ Updated: {filename}")

    count += 1