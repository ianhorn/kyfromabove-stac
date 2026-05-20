import os
import rasterio
import boto3
import pandas as pd
import concurrent.futures


phase = 'dem-phase2'  # update this
product = 'tfw'   # world file
csv = f'csv/{phase}-keys.csv'
bucket = 'kyfromabove'

# get the S3 boto resource
s3 = boto3.resource('s3')

# create a df that reads the csv of aws keys
tifs = pd.read_csv(csv)

def get_geotransform(tif):
    """
    Using rasterio module, this function grabs the GeoTransform information,
    formats it, and returns the values formatted for a world file.  
    """

    # Open the dataset
    with rasterio.open(tif) as dataset:
        transform = dataset.transform
        
        # Extract GeoTransform values
        geotransform_values = [
            transform.a,     # pixel width
            transform.b,     # row rotation (typically zero)
            transform.d,     # column rotation (typically zero)
            transform.e,     # pixel height (usually negative)
            transform.c,     # x-coordinate of center of upper-left pixel
            transform.f      # y-coordinate of center of upper-left pixel
        ]

    return geotransform_values

def create_world_file(tif_key):
    """
    This functions takes the geotransform values and writes them back to 
    the bucket as a world file
    
    The name for the .tfw will the be same key as the tif, but with .tfw
    replacing tif
    """
    try:
        tif_vsis3_path = f'/vsis3/{bucket}/{tif_key}'
        tfw_key = os.path.splitext(tif_key)[0] + '.tfw'

        geotransform = get_geotransform(tif_vsis3_path)
        tfw_content = '\n'.join([f"{v:.10f}" for v in geotransform])

        s3.Object(bucket, tfw_key).put(Body=tfw_content.encode('utf-8'))
        print(f"✅ Uploaded: {tfw_key}")
    except Exception as e:
        print(f"❌ Failed for {tif_key}: {e}")
    
if __name__ == '__main__':
    tif_keys = tifs['key'].tolist()  # assuming the column with S3 keys is named 'Key'

    # Use ThreadPoolExecutor — adjust max_workers as needed
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(create_world_file, key) for key in tif_keys]
        concurrent.futures.wait(futures)        