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

def print_log_messages(msg, logger, is_err=False, verbose=2):
    """
    Print msg and optionally write it to an instance of the casalogger.

    If msg is a list then the elements are each printed first followed by logging each element.

    Messages are normally printed to sys.stdout and logged as INFO to the casalogger.
    
    When is_err is True the message is printed sys.stderr and logged as SEVERE

    When verbose is < 2 then the message is not printed unless there is no logger

    This function is intended for internal casaconfig use.

    Parameters
       - msg (str) - The message to print and optionally log.
       - logger (casatools.logsink) - Instance of the casalogger to use. Not used if None.
       - is_err (bool=False) - When False, output goes to sys.stdout and logged as INFO level. When True, output goes to sys.stderr and logged as SEVERE
       - verbose (int=2) - When < 2 then msg is only printed if there is no logger, otherwise it's just logged

    Returns
       None

    """

    import sys
    fileout = sys.stdout
    loglevel = 'INFO'
    if (is_err):
        fileout = sys.stderr
        loglevel = 'SEVERE'

    # this is rarely called and this should be a fast operation, it makes the code simpler
    if type(msg) is not list:
        msg = [msg]

    # always print if there is no logger, if there is a logger and verbose is < 2 then do not print
    if (logger is None) or (not verbose < 2):
        for m_msg in msg:
            print(m_msg,file=fileout)

    for m_msg in msg:
        if logger is not None: logger.post(m_msg, loglevel)
