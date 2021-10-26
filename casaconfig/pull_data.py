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


def pull_data(path=None, branch=None, logger=None):
    """
    Pull down the package data contents from github to the specified directory

    Parameters
    ----------
    path: str
        Folder path to place casadata contents. Default None places it in package installation directory
    branch : str
        casadata repo branch to retrieve data from. Use 'master' for latest casadata trunk. Default None attempts
        to get data from repo branch matching this installation version.
    logger : casatools.logsink
        Instance of the casalogger to use for writing messages. Default None writes messages to the terminal

    Returns
    -------
    None

    """
    import pkg_resources
    import importlib_metadata
    import git
    import os

    if path is None: path = pkg_resources.resource_filename('casaconfig', '__data__/')
    path = os.path.expanduser(path)
    if not os.path.exists(path): os.mkdir(path)
    if branch is None:
        try:
            branch = 'v'+importlib_metadata.version('casaconfig')
        except:
            branch = 'v0.0.0'

    if logger is None:
        print('Downloading data contents...')
    else:
        logger.post('casaconfig downloading data contents...', 'INFO')

    try:
        repo = git.Repo.clone_from('https://github.com/casangi/casaconfig.git', path+'/tmp', branch=branch)
    except:
        if logger is None:
            print("WARNING: can't find data branch %s, defaulting to master" % branch)
        else:
            logger.post('casaconfig cant find data branch %s, defaulting to master' % branch, 'WARN')

        repo = git.Repo.clone_from('https://github.com/casangi/casaconfig.git', path + '/tmp', branch='master')

    os.system('cp -r %s/tmp/data/* %s' % (path, path))
    os.system('rm -fr %s/tmp' % path)

