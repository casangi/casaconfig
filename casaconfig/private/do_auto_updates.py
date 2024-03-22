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

def do_auto_updates(configDict, logger=None, verbose=None):
    """
    Use measurespath, data_auto_update, and measures_auto_update from configDict to
    do any auto updates as necessary.

    This is intended for use during casatools init but may be useful in other cases.

    Note that the IERS measures data is usually read when casatools starts and so 
    changes made to that table may not be seen until a new session if this function
    is used outside of casatools initialization.

    measurespath must be set (not None).

    measures_auto_update must be True when data_auto_update is True.

    See the documentation for data_update and measures_update for additional details
    about the auto update rules.

    The verbose argument controls the level of information provided when this function when the data
    are unchanged for expected reasons. A level of 0 prints and logs nothing. A
    value of 1 logs the information and a value of 2 logs and prints the information.

    See data_update and measures_update for additional details about exceptions

    Paramters
       - configDict (dict) - A config dictionary previously set. 
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal.
       - verbose (int) - Level of output, 0 is none, 1 is to logger, 2 is to logger and terminal, defaults to casaconfig_verbose in the config dictionary.

    Returns
       None

    Raises
       - casaconfig.UnsetMeasurespath - raised when measurespath is None in config

    """

    from .print_log_messages import print_log_messages
    from .data_update import data_update
    from .measures_update import measures_update

    from casaconfig import UnsetMeasurespath

    if configDict.measurespath is None:
        # continue, because things still might work if there are measures in datapath
        raise UnsetMeasurespath('do_auto_updates: measurespath is None in configDict. Provide a valid path and retry.')

    if verbose is None:
        verbose = configDict.casaconfig_verbose

    if (configDict.measures_auto_update or configDict.data_auto_update):
        if (configDict.data_auto_update and (not configDict.measures_auto_update)):
            print_log_messages('measures_auto_update must be True when data_auto_update is True, skipping auto updates', logger, True)
        else:
            if configDict.data_auto_update:
                data_update(configDict.measurespath, logger=logger, auto_update_rules=True, verbose=verbose)
            if configDict.data_auto_update or configDict.measures_auto_update:
                measures_update(configDict.measurespath, logger=logger, auto_update_rules=True, verbose=verbose)

    return
