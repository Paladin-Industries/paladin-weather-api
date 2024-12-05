import xarray as xr
import rasterio
from rasterio.transform import from_bounds
import os
import pandas as pd

def open_netcdf(file_path):
    """
    Opens a NetCDF file and returns the dataset
    
    Parameters:
    file_path (str): Path to the NetCDF file
    
    Returns:
    xarray.Dataset: Opened dataset
    """
    return xr.open_dataset(file_path)

def get_spatial_info(dataset):
    """
    Extracts spatial information from the dataset
    
    Parameters:
    dataset (xarray.Dataset): Input dataset
    
    Returns:
    tuple: (left, bottom, right, top) bounds and CRS if available
    """
    # Get coordinate information
    try:
        lon = dataset.longitude.values
        lat = dataset.latitude.values
    except AttributeError:
        # Try alternative common coordinate names
        lon = dataset.lon.values if 'lon' in dataset else dataset.x.values
        lat = dataset.lat.values if 'lat' in dataset else dataset.y.values
    
    # Calculate bounds
    left, right = lon.min(), lon.max()
    bottom, top = lat.min(), lat.max()
    
    # Try to get CRS information
    crs = getattr(dataset, 'crs', 'EPSG:4326')  # Default to WGS84 if not specified
    
    return (left, bottom, right, top), crs

def create_raster(data, bounds, output_path, crs='EPSG:4326'):
    """
    Creates a raster file from the data array
    
    Parameters:
    data (numpy.ndarray): 2D array of data
    bounds (tuple): (left, bottom, right, top) bounds
    output_path (str): Path for output raster
    crs (str): Coordinate reference system
    """
    left, bottom, right, top = bounds
    height, width = data.shape
    
    # Create the transform
    transform = from_bounds(left, bottom, right, top, width, height)
    
    # Create the raster
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(data, 1)

def netcdf_to_rasters(netcdf_path, output_dir, variable_name=None):
    """
    Converts NetCDF data to raster files
    
    Parameters:
    netcdf_path (str): Path to NetCDF file
    output_dir (str): Directory for output rasters
    variable_name (str): Optional specific variable to convert
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the dataset
    ds = open_netcdf(netcdf_path)
    
    # Get spatial information
    bounds, crs = get_spatial_info(ds)
    
    # Get variables to process
    if variable_name:
        variables = [variable_name]
    else:
        # Filter out coordinate variables
        variables = [var for var in ds.data_vars 
                    if set(ds[var].dims) & {'latitude', 'longitude', 'lat', 'lon', 'x', 'y'}]
    
    # Process each variable
    for var in variables:
        data = ds[var]
        
        # Handle different dimensional data
        if 'time' in data.dims:
            # Create a raster for each time step
            for time_idx in range(len(data.time)):
                time_value = data.time.values[time_idx]
                time_str = pd.to_datetime(time_value).strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(output_dir, f'{var}_{time_str}.tif')
                
                # Extract 2D slice
                data_slice = data.isel(time=time_idx).values
                create_raster(data_slice, bounds, output_path, crs)
        else:
            # Single time step
            output_path = os.path.join(output_dir, f'{var}.tif')
            create_raster(data.values, bounds, output_path, crs)
    
    ds.close()


netcdf_path = "./data/gfs_20241126_00.nc"
output_dir = "./output"
netcdf_to_rasters(netcdf_path, output_dir)