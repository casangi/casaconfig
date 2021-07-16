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


def table_open(path=None):
    """
    Open a variety of casadata contents

    Parameters
    ----------
    path : str
        Folder path to the data. Default None looks in current working directory

    Returns
    -------
    xarray.core.dataset.Dataset
        xarray dataset or dataset of datasets

    """
    from cngi.conversion import read_table
    import os
    import xarray
    
    if path is None: path = './'
    path = os.path.expanduser(path)
    xds_list = []

    files = os.listdir(path)

    # open specified table
    if 'table.dat' in files:
        xds = read_table(path)
        xds_list += [(path.split('/')[-1], xds)]
    
    # open all tables in specified directory
    else:
        for ff in files:
            if os.path.isdir(os.path.join(path,ff)):
                subfiles = os.listdir(os.path.join(path,ff))
                if 'table.dat' in subfiles:
                    xds = read_table(os.path.join(path,ff))
                    xds_list += [(ff, xds)]

    mxds = None
    if len(xds_list) > 1:
        mxds = xarray.Dataset(attrs=dict(xds_list))
    elif len(xds_list) == 1:
        mxds = xds_list[0]
        
    return mxds
