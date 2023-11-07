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

def read_readme(path):
    """
    Read and parse the contents of a readme.txt file used by casaconfig.

    A dictionary containing the 'version', 'date', and 'extra' (containing
    a list of optional extra lines found). On error, the return values is None.

    The extra lines are stripped and do not include lines begining with '#'

    The format is assumed to be:
        a line begining with #, which is ignored.
        a line "version : the versions string"
        a line "date : the date"
        optional extra lines (the manifest of installed files for the main readme)

    The version string and date are stripped of leading and trailing whitespace.

    Parameters
       - path (str) - the path to the file to be read

    Returns
       Dictionary of 'version' (the version string), 'date' (the date string),
       'extra' (a list of any extra lines found). The return value is None on error.
    """

    import os

    version = ""
    date = ""
    extra = []
    result = None
    
    try:
        with open(path, 'r') as fid:
            readmeLines = fid.readlines()
            version = readmeLines[1].split(':')[1].strip()
            date = readmeLines[2].split(':')[1].strip()
            if len(readmeLines) > 3:
                for extraLine in readmeLines[3:]:
                    if (extraLine[0] != '#'):
                        extra.append(extraLine.strip())
            result = {'version':version, 'date':date, 'extra':extra}
    except:
        pass

    return result
