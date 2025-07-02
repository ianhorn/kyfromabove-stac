"""
Just some helpful lines for my use
"""

    # id = os.path.basename(href)  # Use only the filename as the ID  
    # 
            # id=id,  

# if not os.path.exists(output_dir):
    #     os.makedirs(output_dir) 
    # 
    #     
    # file_path = os.path.basename(href).replace(".tif", ".json")
    # stac_json = os.path.join(output_dir, file_path)

    # # Write the STAC item to a JSON file
    # with open(stac_json, 'w') as f:
    #     json.dump(item.to_dict(), f, indent=4)  # Use `to_dict()` method to serialize
    #     print(f"Saved {stac_json} to file.\n")
    # 
    # 
    #  

curl http://localhost:8000/cog/stac?url=https://kyfromabove.s3.us-west-2.amazonaws.com/imagery/orthos/Phase1/KY_KYAPED_2014_6IN/N135E128_2014_6IN_cog.tif -o file_n
ame.json