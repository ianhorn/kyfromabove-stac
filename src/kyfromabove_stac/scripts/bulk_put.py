import json
import requests
import os
from concurrent.futures import ProcessPoolExecutor

def put_item(args):
    file, phase, acq_phase = args
    api_url_base = "https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/"

    try:
        if acq_phase not in file:
            print(f"⏭️ Skipping {file} (does not match phase '{acq_phase}')")
            return None

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
    phase = "dem-phase2"
    acq_phase = "Phase2"
    folder = "C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/items/dems/"

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".json")
    ]

    # Now include acq_phase in the task list
    tasks = [(f, phase, acq_phase) for f in files]

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(put_item, tasks))

    print("✅ All done.")