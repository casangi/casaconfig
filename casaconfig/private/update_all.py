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

def update_all(path=None, logger=None, force=False):
    """
    Update the data contants at path to the most recently released versions
    of casarundata and measures data. 

    If path does not exist it will be created (the user must have permission
    to create path).

    If path does exist and is not empty it must contain a previously
    installed version of casarundata. Path must be a directory and it
    must be owned by the user.

    If path is not provided then config is imported and the measurespath value set
    by that process will be used.

    If path already contains the most recent versions of casarundata and 
    measurespath then nothing will change at path.

    The force argument is passed to data_update and measures_update

    This uses pull_data, data_update and measures_update. See the
    documentation for those functions for additional details.

    Some of the data updated by this function is only read when casatools starts.
    Use of update_all after CASA has started should typically be followed by a restart 
    so that any changes are seen by the tools and tasks that use this data.

    Parameters
       - path (str=None) - Folder path to place casarundata contents. It must not exist, or be empty, or contain a valid, previously installed version. If it exists, it must be owned by the user. Default None uses the value of measurespath set by importing config.py.
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Messages are always written to the terminal. Default None does not write any messages to a logger.

    Returns
       None

    """

    import os

    from .print_log_messages import print_log_messages
    from .get_data_info import get_data_info
    from .pull_data import pull_data
    from .data_update import data_update
    from .measures_update import measures_update

    if path is None:
        from casaconfig import config
        path = config.measurespath

        if path is None:
            print_log_messages("config.measurespath is None. Edit your config.py to set measurespath to an appropriate location,", logger, True)
            return

    if not os.path.exists(path):
        # create it, all the way down
        try:
            os.makedirs(path, exist_ok=True)
        except:
            print_log_messages("unable to create path, check the permissions of the directory it is being created at, path = %s" % path, logger, True)
            return

    # path must be a directory and it must be owned by the user
    
    if (not os.path.isdir(path)) or (os.stat(path).st_uid != os.getuid()):
        msgs = []
        msgs.append("Warning: path must exist as a directory and it must be owned by the user, path = %s" % path)
        msgs.append("Warning: no updates are possible on this path by this user.")
        print_log_messages(msgs, logger, False)
        return

    # if path is empty, first use pull_data
    if len(os.listdir(path))==0:
        pull_data(path, logger)
        # double check that it's not empty
        if len(os.listdir(path))==0:
            print_log_messages("pull_data failed, see the error messages for more details. update_all can not continue")
            return

    # readme.txt must exist in path at this point, using get_data_info provides more possible feedback
    dataInfo = get_data_info(path, logger)
    if dataInfo is None:
        # this should not happen
        print_log_messages('could not find any data information about %s, can not continue with update_all' % path, logger, True)

    if dataInfo['casarundata'] is None:
        print_log_messages('readme.txt not found at path, update_all can not continue, path = %s' % path, logger)
        return

    if dataInfo['casarundata'] is 'invalid':
        print_log_messages('readme.txt is invalid at path, update_all can not continue, path = %s' % path, logger)
        return

    if dataInfo['casarundata'] is 'unknown':
        print_log_messages('contents at path appear to be casarundata but no readme.txt was found, casaconfig did not populate this data and update_all can not continue, path = %s', path, logger)
        return

    # the updates should work now
    data_update(path, logger, force=force)
    measures_update(path, logger, force=force)

    return
