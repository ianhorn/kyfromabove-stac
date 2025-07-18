import os
from osgeo import gdal

pwd = os.getcwd()
product = "orthos"
phase = "phase1"
csv = f'{pwd}/csv/{product}-{phase}.csv'

# print(f'\n{csv}\n')

