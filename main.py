from os import walk
import pandas as pd
from netCDF4 import Dataset, date2num
from os import path
import numpy as np


def reformat(dirpath, file):

    try:
        in_pth = path.join(dirpath, file)
        out_pth = dirpath + "\\out\\" + file
        timestr = pd.to_datetime(file[11:19], format='%Y%m%d')

        in_DS = Dataset(in_pth, "r", format='NETCDF4')
        # in_DS['NDVI'].set_auto_scale(False)

        out_DS = Dataset(out_pth, "w", format='NETCDF4')

        out_DS.setncatts(in_DS.__dict__)

        # Recreate dimensions
        out_DS.createDimension('lat', in_DS.dimensions['lat'].size)
        out_DS.createDimension('lon', in_DS.dimensions['lon'].size)
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
        NDVI = out_DS.createVariable('NDVI',  np.int32, ('time', 'lat', 'lon'), zlib=True, shuffle=True)

        dict = in_DS.variables['NDVI'].__dict__

        for key, value_orig in dict.items():
            if type(value_orig) == np.uint8:
                dict[key] = np.int32(value_orig)
            elif type(value_orig) == np.ndarray:
                dict[key] = value_orig.astype(np.int32)

        NDVI.setncatts(dict)

        # fill with original values
        out_DS.variables['lat'][:] = in_DS.variables['lat'][:]
        out_DS.variables['lon'][:] = in_DS.variables['lon'][:]

        out_DS.variables['NDVI'][:] = np.expand_dims(in_DS.variables['NDVI'][:], 0)

        out_DS.close()

        return file

    except Exception as e:
        raise e

if __name__ == '__main__':

    mypath = r'Z:\Spot\NDVI_v2.3_s10_1998_2014\NC\test'

    for (dirpath, dirnames, filenames) in walk(mypath):
        break
    print('Files to be processed: {0} \n'.format(len(filenames)))

    for i, file_name in enumerate(filenames):
        reformat(dirpath, file_name)
        print('Time dimension added on :{0}'.format(file_name))
    print('\n All files processed')