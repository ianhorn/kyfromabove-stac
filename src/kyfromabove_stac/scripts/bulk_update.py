import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

FOLDER = Path(r"C:\Users\Ian.Horn\Documents\stac-repos\existing_dem3_items")
NEW_COLLECTION = "dem-phase3-backup"


def update_file(file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Update collection
        data["collection"] = NEW_COLLECTION

        # Clear links
        data["links"] = []

        # Write back to same file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Updated {file_path.name}")

    except Exception as e:
        print(f"❌ Failed {file_path.name}: {e}")


def main():
    files = list(FOLDER.glob("*.json"))
    print(f"Processing {len(files)} files...")

    with ProcessPoolExecutor() as executor:
        executor.map(update_file, files)


if __name__ == "__main__":
    main()