""""
This scripts assigns a yearly temporal extent to KyFromAbove items.
Collections cover more years.  Assign extents by years may allow for 
more filtering by datetime.
"""

from datetime import datetime
import rasterio
from shapely.geometry import mapping, Polygon
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import AssetRasterExtension

def assign_start_datetime(item):
    """
    Assigns temporal extents to collection items.

    Parameters:
        items (str or list): A single href/name or a list of hrefs/names representing 
        the collection items.
    """

    start_datetime = None
    try:
        if "DEM" in item:
            if "Phase1" in item:
                if "2010" in item:
                    return datetime(2010, 3, 18, 0, 0, 0)
                elif "2011" in item:
                    return datetime(2010, 4, 12, 0, 0, 0)
                elif  "2012" in item:
                    return datetime(2012, 3, 12, 16, 18, 0)
                elif "2013" in item:
                    return datetime(2012, 11, 6, 0, 0, 0)
                elif "2014" in item:
                    return datetime(2014, 11, 19, 0, 0, 0)
                elif "2015" in item:
                    return datetime(2015, 4, 11, 0, 0, 0)
                elif "2016" in item:
                    return datetime(2016, 2, 17, 0, 0, 0)
                elif "2017" in item:
                    return datetime(2017, 12, 15, 0, 0, 0)
            elif "Phase2" in item:
                if "2019" in item:
                    return datetime(2019, 2, 19, 0, 0, 0)
                elif "2020" in item:
                    return datetime(2019, 12, 5, 0, 0, 0)
                elif "2021" in item:
                    return datetime(2021, 3, 4, 0, 0, 0)
                elif "2022" in item:
                    return datetime(2022, 2, 7, 0, 0, 0)
                elif "2023" in item:
                    return datetime(2022, 12, 12, 0, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 1, 8, 0, 0, 0)
            elif "Phase3" in item:
                if "2022" in item:
                    return datetime(2022, 2, 7, 0, 0, 0)
                elif "2023" in item:
                    return datetime(2012, 12, 12, 0, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 1, 8, 0, 0, 0)
        elif "orthos" in item:
            if "Phase1" in item:
                if "2012" in item:
                    return datetime(2012, 3, 10, 0, 0, 0)
                elif "2013" in item:
                    return datetime(2013, 4, 3, 0, 0, 0)
                elif "2014" in item:
                    return datetime(2014, 3, 30, 0, 0, 0)
            elif "Phase2" in item:
                if "2019" in item:
                    return datetime(2019, 2, 25, 0, 0, 0)
                elif "2020" in item:
                    return datetime(2020, 3, 4, 0, 0, 0)
                elif "2021" in item:
                    return datetime(2021, 2, 26, 0, 0, 0)
                elif "2022" in item:
                    return datetime(2022, 2, 1, 0, 0, 0)
                elif "2023" in item:
                    return datetime(2023, 2, 1, 0, 0, 0)
            elif "Phase3" in item:
                if "2022_Season2" in item:
                    return datetime(2022, 11, 15, 0, 0, 0)
                elif "2023_Season1" in item:
                    return datetime(2023, 2, 1, 0, 0, 0)
                elif "2023_Season2" in item:
                    return datetime(2023, 11, 15, 0, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 2, 1, 0, 0, 0)

    except Exception as e:
        print(e)    

    return start_datetime.isformat() if start_datetime else None  

def assign_end_datetime(item):
    """
    Assigns temporal extents to collection items.

    Parameters:
        items (str or list): A single href/name or a list of hrefs/names representing 
        the collection items.
    """

    end_datetime = None
    try:
        if "DEM" in item:
            if "Phase1" in item:
                if "2010" in item:
                    return datetime(2010, 6, 7, 0, 0, 0)
                elif "2011" in item:
                    return datetime(2010, 4, 10, 0, 0, 0)
                elif  "2012" in item:
                    return datetime(2013, 4, 8, 10, 11, 0)
                elif "2013" in item:
                    return datetime(2014, 10, 13, 12, 0, 0)
                elif "2014" in item:
                    return datetime(2015, 1, 28, 0, 0, 0)
                elif "2015" in item:
                    return datetime(2016, 1, 2, 12, 0, 0)
                elif "2016" in item:
                    return datetime(2016, 2, 28, 12, 0, 0)
                elif "2017" in item:
                    return datetime(2017, 4, 2, 0, 0, 0)
            elif "Phase2" in item:
                if "2019" in item:
                    return datetime(2019, 3, 23, 12, 0, 0)
                elif "2020" in item:
                    return datetime(2020, 3, 6, 12, 0, 0)
                elif "2021" in item:
                    return datetime(2021, 3, 16, 12, 0, 0)
                elif "2022" in item:
                    return datetime(2022, 4, 14, 12, 0, 0)
                elif "2023" in item:
                    return datetime(2023, 3, 5, 12, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 2, 5, 0, 0, 0)
            elif "Phase3" in item:
                if "2022" in item:
                    return datetime(2022, 4, 14, 0, 0, 0)
                elif "2023" in item:
                    return datetime(2023, 3, 5, 0, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 2, 5, 0, 0, 0)
        elif "orthos" in item:
            if "Phase1" in item:
                if "2012" in item:
                    return datetime(2012, 3, 27, 12, 0, 0)
                elif "2013" in item:
                    return datetime(2013, 7, 20, 12, 0, 0)
                elif "2014" in item:
                    return datetime(2014, 4, 19, 0, 0, 0)
            elif "Phase2" in item:
                if "2019" in item:
                    return datetime(2019, 4, 16, 0, 0, 0)
                elif "2020" in item:
                    return datetime(2020, 4, 10, 0, 0, 0)
                elif "2021" in item:
                    return datetime(2021, 4, 19, 0, 0, 0)
                elif "2022" in item:
                    return datetime(2022, 3, 20, 0, 0, 0)
                elif "2023" in item:
                    return datetime(2023, 4, 1, 0, 0, 0)
            elif "Phase3" in item:
                if "2022_Season2" in item:
                    return datetime(2022, 12, 10, 0, 0, 0)
                elif "2023_Season1" in item:
                    return datetime(2023, 4, 15, 0, 0, 0)
                elif "2023_Season2" in item:
                    return datetime(2023, 12, 12, 0, 0, 0)
                elif "2024" in item:
                    return datetime(2024, 4, 1, 12, 0, 0)
                
    except Exception as e:
        print(e)    

    return end_datetime.isoformat() if end_datetime else None



def assign_collection(href):
    """
    This will assign a collection based on type (imagery/elevation)
    and phase, which is built into the name.
    """
    if "orthos" in href and "Phase1" in href:
        return "orthos-phase1"
    elif "orthos" in href and "Phase2" in href:
        return "orthos-phase2"
    elif "orthos" in href and "Phase3" in href:
        return "orthos-phase3"
    elif "DEM" in href and "Phase1" in href:
        return "dem-phase1"
    elif "DEM" in href and "Phase2" in href:
        return "dem-phase2"
    elif "DEM" in href and "Phase3" in href:
        return "dem-phase3"
    else:
        return None

def get_item_properties(href) -> dict:
    properties = {"license": "CC-BY-4.0"}
    properties = {
        "assets": {
            "href": href,
            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            "roles": "data"
        }
    }

   # add band properties for orthos
    if "orthos" in href:
        eo_bands = {
            "band 1": "red",
            "band 2": "green",
            "band 3": "red",
            "band 4": "nir"
        }
    properties["eo:bands"] = eo_bands
    
    return properties


def get_bbox_and_footprint(raster):
    """
    Example lifted straight from the tutorial on https://stacindex.org/en/tutorials/2-create-stac-catalog-python/index.html

    Parameter: raster (item or href)
    
    """

    with rasterio.open(raster) as r:
        crs = r.crs
        bounds = r.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        
        return (bbox, mapping(footprint), crs)
    

def get_stac_extensions(href):
    extensions = []
    if href.endswith(".tif"):
        extensions.append("projection")  # Projection extension for geospatial data
        extensions.append("raster")      # Raster extension for raster data
    return extensions