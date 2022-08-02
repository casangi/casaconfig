# Copyright 2022 AUI, Inc. Washington DC, USA
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

## get an argparse.ArgumentParser suitable for parsing the configurable
## parameters known to casa, help is turned off here but can be turned on in the returned parser
## this parser includes the arguments used by casaconfig, additional arguments can be added

def get_argparser(add_help=False):
    import argparse as __argparse

    ## look for arguments affecting the configuration
    parser = __argparse.ArgumentParser(add_help=add_help)
    parser.add_argument( "--noconfig", dest='noconfig', action='store_const', const=True, default=False,
                         help='do not load user configuration file' )
    parser.add_argument( "--configfile",dest='configfile', default='~/.casa/config.py',
                         help='location of the user configuration file')
    return parser
