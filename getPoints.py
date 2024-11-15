# imports
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import glob as glob
import datetime as dt
from herbie import Herbie
import numpy as np
import io
import base64
from typing import List
from PIL import Image
from scipy.interpolate import Rbf

# get points just outputs gridded temperature, wxPal outputs a json converted image
def get_weather_raster(south_east: List[float], north_west: List[float], time_interval: List[int], colormap: str = 'viridis', dpi: int = 100) -> Image.Image:
    points = get_points(south_east, north_west, time_interval)

    lats = np.array([p[0] for p in points])
    lons = np.array([p[1] for p in points])
    values = np.array([p[2] for p in points])

    grid_lon, grid_lat = np.meshgrid(
        np.linspace(lons.min(), lons.max(), 100),
        np.linspace(lats.min(), lats.max(), 100)
    )

    rbf = Rbf(lons, lats, values, function='linear')
    grid_values = rbf(grid_lon, grid_lat)

    print(grid_values)

    plt.ioff()
    fig = plt.figure(figsize=(10, 10), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])

    img = ax.imshow(
        grid_values,
        extent=[lons.min(), lons.max(), lats.min(), lats.max()],
        origin="lower",
        cmap=colormap,
        aspect="auto",
        interpolation="nearest",
        vmin=values.min(),
        vmax=values.max()
    )
    
    ax.axis("off")

    fig.canvas.draw()

    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    buf.shape = (h, w, 3)

    plt.close(fig)

    image = Image.fromarray(buf)

    return image

def get_points(south_east: List[float], north_west: List[float], time_interval: List[int]) -> List[List[float]]:
    
    latr = [south_east[0], north_west[0]]
    lonr = [north_west[1], south_east[1]]
    fcst_hr = time_interval[0]

    print("latr", latr)
    print("lonr", lonr)
    print("fcst_hr", fcst_hr)

    op_time = dt.datetime.now()
    
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
    # variable = H.xarray(":RH:2 m").rh2m

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

    longitude_values = hxm.values.tolist()
    latitude_values = hym.values.tolist()
    temperature_values = variablem.values.tolist()
    
    assembled_list = []
    for i in range(len(longitude_values)):
        for j in range(len(longitude_values[i])):
            assembled_list.append([latitude_values[i][j], longitude_values[i][j], temperature_values[i][j]])

    return assembled_list

# read specific area of a hrrr output at a specific ti

def WxPal(south_east: List[float], north_west: List[float], time_interval: List[int]) -> List[List[float]]:
    
    latr = [south_east[0], north_west[0]]
    lonr = [north_west[1], south_east[1]]
    fcst_hr = time_interval[0]

    op_time = dt.datetime.now()
    
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

    plt.pcolormesh(hxm,hym,variablem)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


# plt.xlim(lor)
# plt.ylim(lar)
# cax.set_clim(20,500)


