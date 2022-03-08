# Copyright 2020 AUI, Inc. Washington DC, USA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
this module will be included in the api
"""
import os
import numpy as np



##################################################################
# read casacore table format in to memory
##################################################################
def read_simple_table(infile):
    from casacore import tables
    import xarray

    tb_tool = tables.table(infile, readonly=True, lockoptions={'option': 'usernoread'}, ack=False)
    if tb_tool.nrows() == 0:
        tb_tool.close()
        return xarray.Dataset()

    dims = ['d%i' % ii for ii in range(20)]
    
    cols = tb_tool.colnames()
    mvars, mcoords, xds = {}, {}, xarray.Dataset()

    tr = tb_tool.row([], exclude=True)[:]

    # extract data for each col
    for col in cols:
        if tb_tool.coldatatype(col) == 'record': continue   # not supported

        try:
            data = np.stack([rr[col] for rr in tr])
            if isinstance(tr[0][col], dict):
                data = np.stack([rr[col]['array'].reshape(rr[col]['shape']) if len(rr[col]['array']) > 0 else np.array(['']) for rr in tr])
        except:
            # sometimes the columns are variable, so we need to standardize to the largest sizes
            if len(np.unique([isinstance(rr[col], dict) for rr in tr])) > 1: continue   # can't deal with this case
            mshape = np.array(np.max([np.array(rr[col]).shape for rr in tr], axis=0))
            data = np.stack([np.pad(rr[col] if len(rr[col]) > 0 else np.array(rr[col]).reshape(np.arange(len(mshape))*0),
                                    [(0, ss) for ss in mshape - np.array(rr[col]).shape], 'constant', constant_values=np.nan) for rr in tr])

        if len(data) == 0: continue
        if col.upper().endswith('_ID'):
            mcoords[col.lower()] = xarray.DataArray(data, dims=['d%i_%i' % (di, ds) for di, ds in enumerate(np.array(data).shape)])
        else:
            mvars[col.upper()] = xarray.DataArray(data, dims=['d%i_%i'%(di,ds) for di, ds in enumerate(np.array(data).shape)])

    xds = xarray.Dataset(mvars, coords=mcoords)
    xds = xds.rename(dict([(dv, dims[di]) for di, dv in enumerate(xds.dims)]))
    bad_cols = list(np.setdiff1d([dv.lower() for dv in tb_tool.colnames()], [dv.lower() for dv in list(xds.data_vars)+list(xds.coords)]))

    attrs = {}
    if len(bad_cols) > 0: attrs['bad_cols'] = bad_cols

    # add table keywords to attributes
    kwd = tb_tool.getkeywords()
    for kk in kwd:
        attrs[kk.lower()] = kwd[kk]

    # add column keywords to attributes
    for col in tb_tool.colnames():
        kwd = tb_tool.getcolkeywords(col)
        for kk in kwd:
            attrs['%s_%s'%(col.lower(),kk.lower())] = kwd[kk]

    xds = xds.assign_attrs(attrs)
    tb_tool.close()

    return xds




def table_open(path=None):
    """
    (addon) Open a variety of casadata contents.

    This function depends on the python-casacore package which **must be manually (pip) installed by the user**

    Parameters
       - path (str=None) - Folder path to the data. Default None looks in current working directory

    Returns
        xarray.core.dataset.Dataset - xarray dataset or dataset of datasets

    """
    import importlib.util
    import xarray

    if importlib.util.find_spec('casacore') is None:
        print("### python-casacore not found ### - try installing with '$: pip install python-casacore'")
        return xarray.Dataset()

    if path is None: path = './'
    path = os.path.expanduser(path)
    xds_list = []

    files = os.listdir(path)

    # open specified table
    if 'table.dat' in files:
        xds = read_simple_table(path)
        xds_list += [(path.split('/')[-1], xds)]
    
    # open all tables in specified directory
    else:
        for ff in files:
            if os.path.isdir(os.path.join(path,ff)):
                subfiles = os.listdir(os.path.join(path,ff))
                if 'table.dat' in subfiles:
                    xds = read_simple_table(os.path.join(path,ff))
                    xds_list += [(ff, xds)]

    mxds = None
    if len(xds_list) > 1:
        mxds = xarray.Dataset(attrs=dict(xds_list))
    elif len(xds_list) == 1:
        mxds = xds_list[0][1]
        
    return mxds
