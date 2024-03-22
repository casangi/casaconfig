# Copyright 2024 AUI, Inc. Washington DC, USA
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

def summary(configDict = None):
    """
    Summarize the configure status.

    This prints out the config files that were loaded successfully, the files are shown by 
    type (default, site, user), the command flags are shown that control whether the site 
    and user config files are used, any errors encountered while loading are printed, the
    value of the measurespath config value is shown, the installed data versions are shown
    (casarundata and measures) and any release version information is shown.

    Parameters
        - configDict (dict) - a config dictionary. If None this is imported from casaconfig.

    Returns
        None

    """

    import casaconfig

    if configDict is None:
        from casaconfig import config as configDict

    try:
        dataInfo = casaconfig.get_data_info()
    except casaconfig.UnsetMeasurespath:
        print("Measurespath is unset or does not exist in config dictionary. Use a valid path and try again")
        return
    
    print("")
    print("casaconfig summary")
    print("")
    print("loaded config files : ")
    for f in configDict.load_success():
        print("   %s" % f)
    if len(configDict.load_failure()) > 0:
        print("")
        print("config failures :")
        for f in configDict.load_failure():
            print("\n%s :" % f)
            print(configDict.load_failure()[f])
    print("")
    if (configDict.__flags.noconfig):
        print("--noconfig option was used")
    if (configDict.__flags.nositeconfig):
        print("--nositeconfig option was used")
    print("")
    print("measurespath : %s" % configDict.measurespath)
    print("")
    if (dataInfo['casarundata'] is None):
        print("casarundata version : no casarundata found")
    else:
        rundataVers = dataInfo['casarundata']['version']
        msg = "casarundata version : %s" % rundataVers
        if rundataVers == "unknown":
            msg += "; legacy data not maintained by casaconfig"
        elif rundataVers == "error":
            msg += "; unexpected readme.txt file, casarundata should be reinstalled"
        print(msg)
    if (dataInfo['measures'] is None):
        print("measures version : no measures found")
    else:
        measVers = dataInfo['measures']['version']
        msg = "measures version : %s" % measVers
        if measVers == "unknown":
            msg += "; legacy data not maintained by casaconfig"
        elif measVers == "error":
            msg += "; unexpected readme.txt file, measures should be reinstalled"
        print(msg)
    
    if (dataInfo['release'] is None):
        print("no release version information found")
    else:
        print('release casarundata version : %s' % dataInfo['release']['casarundata'])
        print('release measures version : %s' % dataInfo['release']['measures'])
    print("")
