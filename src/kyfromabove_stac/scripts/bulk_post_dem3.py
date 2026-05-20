import json
import asyncio
from pathlib import Path
import aiohttp


PHASE = "orthos-phase2"
FOLDER = Path(r"C:/Users/Ian.Horn/Documents/stac-repos/items/PHASE}")

API_URL_BASE = "https://drwgni8q1h.execute-api.us-west-2.amazonaws.com/collections/"

POST_URL = f"{API_URL_BASE}{PHASE}/items"

# Limit concurrency (tune this: 10–50 is usually safe)
SEM = asyncio.Semaphore(28)


async def post_item(session, file_path):
    async with SEM:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                item = json.load(f)

            async with session.post(
                POST_URL,
                json=item,
                headers={"Content-Type": "application/json"},
            ) as response:

                if response.status in (200, 201):
                    print(f"✅ {file_path.name}")
                else:
                    text = await response.text()
                    print(f"❌ {file_path.name} → {response.status}")
                    print(text)

        except Exception as e:
            print(f"💥 Error with {file_path.name}: {e}")


async def main():
    files = list(FOLDER.glob("*.json"))
    print(f"Uploading {len(files)} files to {POST_URL}")

    async with aiohttp.ClientSession() as session:
        tasks = [post_item(session, f) for f in files]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())