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


def pull_data(path=None, branch=None, force=False, logger=None):
    """
    Pull down the package data contents from github to the specified directory

    The package installation directory (returned by get_data_dir()) is used when 
    path is not specified. Note that that location need not be the same as 
    datapath. 

    The measures tables included in the package data at github will typically 
    not be the most recent versions. If measurespath is the same as path then 
    measures_update() should be used after pull_data to get the most recent 
    measures tables. If measurespath is a different directory then the measures
    table found there are always used even if measures tables are also found
    at other locations in datapath.

    Some of the tables installed by pull_data are only read when casatools
    starts. Use of pull_data (or measures_update) should typically be followed
    by a restart so that any changes are seen by the tools and tasks that
    use this data.

    Parameters
       - path (str=None) - Folder path to place casadata contents. Default None places it in package installation directory
       - branch (str=None) - casadata repo branch to retrieve data from. Use 'master' for latest casadata trunk. Default None attempts
         to get data from repo branch matching this installation version.
       - force (bool=False) - If True, always re-download the data even if already present in path. Default False will not download data if already populated
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal

    Returns
       None

    """
    import pkg_resources
    import importlib_metadata
    import git
    import os
    import numpy as np
    import sys

    if path is None: path = pkg_resources.resource_filename('casaconfig', '__data__/')
    path = os.path.expanduser(path)
    if not os.path.exists(path): os.mkdir(path)
    if branch is None:
        try:
            branch = 'v'+importlib_metadata.version('casaconfig')
        except:
            branch = 'v0.0.0'

    # check contents of destination folder
    expected = ['catalogs', 'demo', 'geodetic', 'alma', 'nrao', 'ephemerides', 'telescope_layout', 'dish_models', 'gui']
    if (len(np.setdiff1d(expected, os.listdir(path))) == 0) and (force == False):
        print('casaconfig found populated data folder %s' % path, file = sys.stderr )
        if logger is not None: logger.post('casaconfig found populated data folder %s' % path, 'INFO')
        return

    print('casaconfig downloading data contents to %s ...' % path, file = sys.stderr )
    if logger is not None: logger.post('casaconfig downloading data contents to %s ...' % path, 'INFO')

    try:
        repo = git.Repo.clone_from('https://github.com/casangi/casaconfig.git', path+'/tmp', branch=branch)
    except:
        if logger is not None: logger.post('casaconfig cant find data branch %s, defaulting to master' % branch, 'WARN')
        else: print("WARNING: can't find data branch %s, defaulting to master" % branch, file = sys.stderr )

        repo = git.Repo.clone_from('https://github.com/casangi/casaconfig.git', path + '/tmp', branch='master')

    os.system('cp -r %s/tmp/data/* %s' % (path, path))
    os.system('rm -fr %s/tmp' % path)
