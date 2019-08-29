import pandas as pd
from netCDF4 import Dataset, date2num
import os
import numpy as np
import xarray as xr


def output_creator(out_path, o_file):
    out_DS = Dataset(out_path, "w", format='NETCDF4')

    out_DS.setncatts(in_DS.__dict__)

    # Recreate dimensions
    out_DS.createDimension('lat', in_DS.dimensions['x'].size)
    out_DS.createDimension('lon', in_DS.dimensions['y'].size)
    out_DS.createDimension("time", None)

    # Create and Fill time variable
    time = out_DS.createVariable("time", "f4", ("time",))
    time.long_name = 'time'
    time.units = "seconds since 1970-01-01 00:00:00.0"
    time.calendar = "gregorian"
    time[:] = date2num(timestr.to_pydatetime(), units=time.units, calendar=time.calendar)

    # Create and fill crs variable
    crs = out_DS.createVariable('crs', 'S1')
    crs.setncatts(in_DS.variables['crs'].__dict__)

    # Create and fill lat long variables
    lat = out_DS.createVariable('lat', in_DS.variables['lat'].dtype, in_DS.variables['lat'].dimensions)
    lat.setncatts(in_DS.variables['lat'].__dict__)
    lan = out_DS.createVariable('lon', in_DS.variables['lon'].dtype, in_DS.variables['lon'].dimensions)
    lan.setncatts(in_DS.variables['lon'].__dict__)

    # Create and fill NDVI variable
    NDVI = out_DS.createVariable('NDVI', np.int32, ('time', 'lat', 'lon'), zlib=True, shuffle=True)

    dict = in_DS.variables['NDVI'].__dict__

    return out_DS


def reformat(dirpath, file, out_dir, o_files):

    try:
        in_pth = os.path.join(dirpath, file)
        name = file[:-5] + '.nc'
        out_path = os.path.join(out_dir, name)

        timestamp = pd.to_datetime(file[16:24], format='%Y%m%d')

        if name in o_files:
           return

        da = xr.open_rasterio(in_pth, "r")
        # in_DS['NDVI'].set_auto_scale(False)
        da = da.assign_coords(time=(pd.to_datetime(timestamp, format='%Y%m%d')))
        da = da.drop('band')
        da = da.expand_dims('time')
        da = da.squeeze('band')
        da = da.rename({'x': 'lat', 'y': 'lon'})
        da.name = 'NDVI'

        da.to_netcdf(out_path, format='NETCDF4', encoding={'NDVI': {'zlib': True,'complevel': 5}})

        # out_DS = output_creator(out_path)
        #
        # for key, value_orig in dict.items():
        #     if type(value_orig) == np.uint8:
        #         dict[key] = np.int32(value_orig)
        #     elif type(value_orig) == np.ndarray:
        #         dict[key] = value_orig.astype(np.int32)
        #
        # NDVI.setncatts(dict)
        #
        # # fill with original values
        # out_DS.variables['lat'][:] = in_DS.variables['lat'][:]
        # out_DS.variables['lon'][:] = in_DS.variables['lon'][:]
        #
        # out_DS.variables['NDVI'][:] = np.expand_dims(in_DS.variables['NDVI'][:], 0)
        #
        # out_DS.close()

    except Exception as e:
        raise e


if __name__ == '__main__':

    path = r'E:\test'
    out_dir = r'E:\test\out'

    for subdir, dirs, files in os.walk(out_dir):
        o_files = files

    for subdir, dirs, files in os.walk(path):
        strings = ['_unc_', 'NOBS', 'QFLAG', 'TGRID', 'pdf']
        for file in files:
            if not any(s in file for s in strings):
                reformat(subdir, file, out_dir, o_files)

    print('\n All files processed')