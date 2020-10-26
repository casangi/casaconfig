#Sekhar et al 2020 in Preperation explains model.
#The column headings are assumed to be stokes,freq,ind,real,imag
def csv_to_zarr(filename,freq_to_hertz):
    from cngi.dio import write_zarr
    import xarray as xr
    import numpy as np
    import dask.array as da
    import csv
    from datetime import date
    
    csv_list = []
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(csvreader) #Heading ['#stokes,freq,ind,real,imag']
        for row in csvreader:
            csv_list.append(np.array(row,float))
            
    csv_array = np.array(csv_list)

    pol_codes = np.unique(csv_array[:,0]).astype(int)
    chan_freq = np.unique(csv_array[:,1])
    num_coef = int(np.max(csv_array[:,2]))+1
    
    zc_array =  np.zeros((len(pol_codes),len(chan_freq),num_coef),dtype=complex)
    
    for i_csv in range(len(csv_array)):
        i_pol = np.where(pol_codes == csv_array[i_csv,0])[0][0]
        i_chan = np.where(chan_freq == csv_array[i_csv,1])[0][0]
        i_coef = int(csv_array[i_csv,2])
        zc_array[i_pol,i_chan,i_coef] =  csv_array[i_csv,3] + 1j*csv_array[i_csv,4]
    
    zc_dataset = xr.Dataset()
    coords = {'pol':pol_codes,'chan':chan_freq*freq_to_hertz,'coef_indx':np.arange(num_coef)}
    zc_dataset = zc_dataset.assign_coords(coords)
    zc_dataset['ZC'] = xr.DataArray(zc_array, dims=['pol','chan','coef_indx'])
    zc_dataset.attrs['name'] = 'MeerKAT_avg_zcoeffs_LBand_lookup'
    zc_dataset.attrs['conversion_date'] = str(date.today())
    
    write_zarr(zc_dataset,filename.split('.')[0]+'.zpc.zarr')
    
'''
if __name__ == '__main__':
    #Remove all . in name except for last (before .csv)
    filenames = ['data/EVLA_avg_SBand_coeffs_highoversamp_wideband.csv','data/EVLA_avg_zcoeffs_LBand_lookup.csv','data/EVLA_avg_zcoeffs_SBand_lookup.csv', 'data/MeerKAT_avg_zcoeffs_LBand_lookup.csv']
    freq_to_hertz = 10**6
    for filename in filenames:
        csv_to_zarr(filename,freq_to_hertz)
'''
