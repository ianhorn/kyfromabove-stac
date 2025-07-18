import os
import rasterio
import boto3
import pandas as pd

phase = 'phase1'  # update this
product = 'tfw'
csv = f'csv/orthos-{phase}.csv'

tifs = pd.read_csv(csv)

def create_tfw(tif):


    # Open the dataset
    with rasterio.open(tif) as dataset:
        if os.path.exists(output_tfw):
            transform = dataset.transform

            # Extract GeoTransform values
            tfw_values = [
                transform.a,     # pixel width
                transform.b,     # row rotation (typically zero)
                transform.d,     # column rotation (typically zero)
                transform.e,     # pixel height (usually negative)
                transform.c,     # x-coordinate of center of upper-left pixel
                transform.f      # y-coordinate of center of upper-left pixel
            ]

            # Write values to a .tfw file
            with open(output_tfw, 'w') as f:
                for value in tfw_values:
                    f.write(f"{value}\n")

    print(f".tfw file created: {output_tfw}")
