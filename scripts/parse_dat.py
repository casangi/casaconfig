import pandas as pd
import os
import numpy as np

np_list = []

files = os.listdir('data/alma/SolarSystemModels')
for ff in files:
    pdf = pd.read_csv('data/alma/SolarSystemModels/'+ff, skiprows=1, delim_whitespace=True, error_bad_lines=False, warn_bad_lines=True)
    #test = np.genfromtxt('data/alma/SolarSystemModels/' + ff, skip_header=1)
    np_list += [pdf.values]
    
    
#np.savez_compressed('test.npz', a=pdf.values)