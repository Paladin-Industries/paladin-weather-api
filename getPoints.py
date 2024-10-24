from typing import List
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cpf
import glob as glob
import os
import pandas as pd
import datetime as dt
from herbie import Herbie,wgrib2
import numpy.ma as ma
import numpy as np
from calendar import monthrange 

# new code

def get_points(south_east: List[float], north_west: List[float], time_interval: List[int]) -> List[List[float]]:
    
    R = 287.058 # gas constant dry air
    # initialize a single HRRR read in
    datestr = str(op_time-dt.timedelta(hours=6))[0:16] # subtract 6 hours from the current time to guarantee a GFS output has populated
    daten = datestr[:10] # current date in string form
    timen = datestr[11:] # current time - 6 hours in string form
    z12 = " 12:00" # string to pull 12Z output
    z00 = " 00:00" # string to pull 00Z output
    print("todays run is from " + daten+z12+' UTC') # indicate what output is being pulled to the terminal
    hdt = daten + z12 # concatenate date for herbie to read model run date 
    opt = [0]#range(0,37)
    model_name = "hrrr"
    product_name = "sfc"
    # opt = range(0,240,3)
    H = Herbie(
        # "2023-10-26 12:00",  # model run date
        hdt,
        model=model_name,  # model name
        product=product_name,  # model product name (model dependent)
        fxx=fcst_hr,  # forecast lead time # <------ for the forecast, loop over times then append GFS to end for long range
    )

    dimen = H.xarray(":HGT:\d+ mb")
    hx = dimen.longitude-360
    hy = dimen.latitude
    variable = H.xarray(":TMP:2 m").t2m

    lat_log = (hy>latr[0]) & (hy<latr[1])
    lon_log = (hx>lonr[0]) & (hx<lonr[1])
    co_log = lat_log & lon_log
    
    rows, cols = np.where(co_log)

    # Find the minimum and maximum row and column indices to form the bounding box
    row_min, row_max = rows.min(), rows.max()
    col_min, col_max = cols.min(), cols.max()

  # Extract the bounded subarray from the original array
    hxm = hx[row_min:row_max+1, col_min:col_max+1]
    hym = hy[row_min:row_max+1, col_min:col_max+1]
    variablem = variable[row_min:row_max+1, col_min:col_max+1]
    
    return hxm,hym,variablem