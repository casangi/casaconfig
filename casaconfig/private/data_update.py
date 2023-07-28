# Copyright 2023 AUI, Inc. Washington DC, USA
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

def data_update(path, auto_update_rules=False, version=None, force=False, logger=None):
    """
    Retrieve the casarundata from the CASA server and install it in path

    See the External Data section in casadocs for more information about the data retrieved.
    This retrieves the full set of CASA runtime data, including the measures data available
    when the requested version of casarundata was produced.
    
    A text file (readme.txt in top-level directory at path) records the version string
    and the date when that version was installed in path.

    If the version requested matches the one in that text file then this function does
    nothing unless force is True.

    If a specific version is not requested (the default) and the date in that text file
    is today, then this function does nothing unless force is True even if there is a more
    recent version available from the CASA server.

    A file lock is used to prevent more that one data_update and measures_update from updating
    any files in path at the same time. When locked, the lock file (datea_update.lock 
    in path) will contain information about the process that has the lock. When a data_update
    gets the lock it will check the readme.txt file in path to make sure that an update is still 
    necessary (if force is True then an update always happens).

    Some of the tables installed by data_update are only read when casatools starts. Use of 
    data_update should typically be followed by a restart of CASA so that any changes are seen by
    the tools and task that use this data.

    **Note:** data_update requires that the expected readme.txt file already exists at the top-level
    directory at path. If the file does not exist or can not be interpreted as expected then
    data_update will return without updating any data.

    **Note:** if auto_update_rules is True the user must own path (in addition to having read and
    write permissions there). The version must then also be None and the force option must be False.

    **Note:** the most recent casarundata may not include the most recent measures data. A data_update
    is typically followed by a measures update.

    Parameters
       - path (str) - Folder path to update. Must contain a valid readme.txt,
       - auto_update_rules (bool=False) - If True then the user must be the owner of path, version must be None, and force must be False.
       - version (str=None) - Version of casarundata to retrieve (usually in the form of casarundata-x.y.z.tar.gz, see data_available()). Default None retrieves the latest.
       - force (bool=False) - If True, always re-download the casarundata. Default False will not download casarundata if already updated today unless the version parameter is specified and different from what was last downloaded.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal.
        
    Returns
       None
    
    """

    print("Not yet implemented, nothing has been updated or checked.")
    return
