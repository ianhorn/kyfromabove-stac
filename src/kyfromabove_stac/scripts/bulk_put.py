import json
import requests
import os
from concurrent.futures import ProcessPoolExecutor

def put_item(args):
    file, phase, = args
    api_url_base = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/"

    try:
        item_list = []

        with open(file, "r", encoding="utf-8") as f:
            item = json.load(f)

        item_id = item["id"]
        put_url = f"{api_url_base}{phase}/items/{item_id}"

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

        return response.status_code

    except Exception as e:
        print(f"❌ Error with file {file}: {e}")
        return None


if __name__ == "__main__":
    phase = "orthos-phase2"
    folder = f"C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/{phase}/"

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".json")
    ]

    tasks = [(f, phase) for f in files]

    with ProcessPoolExecutor(max_workers=18) as executor:
        results = list(executor.map(put_item, tasks))

    print("✅ All done.")