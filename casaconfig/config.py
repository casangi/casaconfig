import os
import time
import sys
import pkg_resources
from casaconfig import measures_update, pull_data


########################################################################
## Setup the runtime operation data directories
########################################################################
datapath = [pkg_resources.resource_filename('casaconfig', '__data__/')]
rundata = os.path.expanduser("~/.casa/measures")

########################################################################
## Define the logfile naming scheme
########################################################################
logfile='casalog_%s.log' % time.strftime("%Y-%m-%d", time.localtime())

########################################################################
## Define what happens when CASA starts
########################################################################
## execute only when casatools is initialized
if __name__.startswith('casatool'):
    from casatools import logsink
    logger = logsink(logfile)

    ########################################################################
    ## Default startup log information
    ########################################################################
    logger.post('########################################################################', 'INFO')
    logger.post('Using default config.py from casaconfig', 'INFO')
    logger.post('python version %s' % sys.version, 'INFO')
    logger.post('########################################################################', 'INFO')

    ########################################################################
    ## Create a ~/.casa folder if not already present
    ########################################################################
    if not os.path.exists(os.path.expanduser("~/.casa")):
        os.system('mkdir %s' % os.path.expanduser("~/.casa"))

    ########################################################################
    ## populate the operational __data__ folder if empty
    ########################################################################
    if len(os.listdir(datapath[0])) == 1:
        pull_data(datapath[0], logger=logger)

    ########################################################################
    ## update the IERS measures data if not already done today
    ########################################################################
    measures_update(rundata, logger=logger)


########################################################################
## Rest of the default CASA configuration parameters
########################################################################
telemetry_enabled = True
crashreporter_enabled = True
nologfile = False
log2term = True
nologger = True
nogui = False
colors = "LightBG"
agg = False
pipeline = False
iplog = True
user_site = False
telemetry_log_directory = "~/tmp"
telemetry_log_limit = 1650
telemetry_log_size_interval = 30
telemetry_submit_interval = 20

