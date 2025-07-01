""""
This scripts assigns a yearly temporal extent to KyFromAbove urls.
Collections cover more years.  Assign extents by years may allow for 
more filtering by datetime.
"""

def assign_datetime(url):
    try:
        if "Phase1" in url:
            if "2010" in url:
                return "2010-03-18/2010-06-07"
            elif "2011" in url:
                return "2011-04-12/2011-04-10"
            elif "2012" in url:
                return "2012-11-06/2013-04-08"
            elif "2013" in url:
                return "2012-11-06/2014-10-13"
            elif "2014" in url:
                return "2014-11-19/2015-01-28"
            elif "2015" in url:
                return "2015-04-11/2016-01-02"
            elif "2016" in url:
                return "2016-02-17/2016-02-28"
            elif "2017" in url:
                return "2016-12-15/2017-04-02"
        elif "Phase2" in url:
            if "2019" in url:
                return "2019-02-19/2019-03-23"
            elif "2020" in url:
                return "2019-12-05/2020-03-16"
            elif "2021" in url:
                return "2021-03-04/2021-03-16"
            elif "2022" in url:
                return "2022-02-07/2022-02-05"
            elif "2023" in url:
                return "2022-12-12/2023-03-05"
            elif "2024" in url:
                return "2024-01-08/2024-02-05"
        elif "Phase3" in url:
            if "2022" in url:
                return "2022-02-07/2022-04-14"
            elif "2023" in url:
                return "2022-12-12/2023-03-05"
            elif "2024" in url:
                return "2024-01-08/2024-02-05"
        elif "orthos" in url:
            if "Phase1" in url:
                if "2012" in url:
                    return "2012-03-10/2012-03-27"
                elif "2013" in url:
                    return "2013-04-03/2013-04-20"
                elif "2013" in url:
                    return "2014-03-30/2014-04-19"
            elif "Phase2" in url:
                if "2019" in url:
                    return "2019-02-25/2019-04-16"
                elif "2020" in url:
                    return "2020-03-04/2020-04-10"
                elif "2021" in url:
                    return "2021-02-16/2021-04-19"
                elif "2022" in url:
                    return "2022-02-01/2022-03-20"
                elif "2023" in url:
                    return "2023-04-01/2023-04-01"
            elif "Phase3" in url:
                if "2022_Season2" in url:
                    return "2022-11-15/2022-12-10"
                elif "2023_Season1" in url:
                    return "2023-02-01/2023-04-15"
                elif "2023_Season2" in url:
                    return "2023-11-15/2023-12-12"
                elif "2024" in url:
                    return "2024-02-01/2024-04-01"

    except Exception as e:
        print(e)

    return url_datetime

def assign_collection(url):
    """
    This will assign a collection based on type (imagery/elevation)
    and phase, which is built into the name.
    """
    if "orthos" in url and "Phase1" in url:
        return "orthos-phase1"
    elif "orthos" in url and "Phase2" in url:
        return "orthos-phase2"
    elif "orthos" in url and "Phase3" in url:
        return "orthos-phase3"
    elif "DEM" in url and "Phase1" in url:
        return "dem-phase1"
    elif "DEM" in url and "Phase2" in url:
        return "dem-phase2"
    elif "DEM" in url and "Phase3" in url:
        return "dem-phase3"
    else:
        return None