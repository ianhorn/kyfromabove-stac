""""
Script to leverage src/kyfromabove-stac/stac.py script

"""
import json
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
from stac_rio import create_item

input_file = "C:/Users/Ian.Horn/Documents/stac-repos/kyfromabove-stac/csv/dem_urls.csv"

output_dir = "../items/dems"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
data = pd.read_csv(input_file)

# Function to create and save STAC items as JSON
def process_row(row):
    href = row["url"]
    stac_item = create_item(href)  # Assuming this returns a STAC item object
    
    # Define the output file path (using the STAC item ID or another unique identifier)
    file_name = f"{stac_item.id}.json"
    file_path = os.path.join(output_dir, file_name)
    
    # Save the STAC item as a JSON file
    with open(file_path, 'w') as f:
        json.dump(stac_item.to_dict(), f, indent=2)
    
    print(f"STAC item created and saved for: {href}")

# Using ThreadPoolExecutor to run tasks concurrently
with ThreadPoolExecutor(max_workers=32) as executor:
    # Pass the rows of the dataframe to the executor
    executor.map(process_row, [row for _, row in data.iterrows()])