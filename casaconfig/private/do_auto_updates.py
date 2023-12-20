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

def do_auto_updates(configDict, logger=None):
    """
    Use measurespath, data_auto_update, and measures_auto_update from configDict to
    do any auto updates as necessary.

    This is intended for use during casatools init but may be useful in other cases.

    Note that the IERS measures data is usually read when casatools starts and so 
    changes made to that table may not be seen until a new session.

    measurespath must be set (not None).

    measures_auto_update must be True when data_auto_update is True

    See the documentation for data_update and measures_update for additional details
    about the auto update rules.

    Paramters
       - configDict (dict) - A config dictionary previously set. 
       - logger (casatools.logsink=None) - Instance of the casalogger to use for writing messages. Default None writes messages to the terminal.

    Returns
       None

    """

    from .print_log_messages import print_log_messages
    from .data_update import data_update
    from .measures_update import measures_update
    
    if configDict.measurespath is None:
        # likely still unset in casasiteconfig.py, suggest setting it in ~/.casa/config.py
        # or ask the site administrator (which may be the user) to edit casasiteconfig.py
        # point at the documentation
        # continue, because things still might work if there are measures in datapath
        print_log_messages('measurespath is None in config', logger, True)
        print_log_messages('this likely means a casasiteconfig.py was used and measurespath remains unset there.', logger, True)
        print_log_messages('Either set measurespath in your config file at ~/.casa/config.py', logger, True)
        print_log_messages('or ask the site manager to set that in casasiteconfig.py', logger, True)
        print_log_messages('visit https://casadocs.readthedocs.io/en/stable/notebooks/external-data.html for more information', logger, True)

        if (configDict.measures_auto_update or configDict.data_auto_update):
            print('\nAuto updates of measures path are not possible because measurespath is not set, skipping auto updates', logger, True)

        return

    if (configDict.measures_auto_update or configDict.data_auto_update):
        if (configDict.data_auto_update and (not configDict.measures_auto_update)):
            print_log_messages('measures_auto_update must be True when data_auto_update is True, skipping auto updates', logger, True)
        else:
            if configDict.data_auto_update:
                data_update(configDict.measurespath, logger=logger, auto_update_rules=True)
            if configDict.data_auto_update or configDict.measures_auto_update:
                measures_update(configDict.measurespath, logger=logger, auto_update_rules=True)

    return
