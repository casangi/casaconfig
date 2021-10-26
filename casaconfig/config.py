import os
import time
import sys
import pkg_resources
from casaconfig import measures_update


########################################################################
## Setup the runtime operation data directories
########################################################################
datapath = [pkg_resources.resource_filename('casaconfig', '__data__/')]
rundata = os.path.expanduser("~/.casa/measures")
logfile='casalog_%s.log' % time.strftime("%Y-%m-%d", time.localtime())

# execute only when casatools is initialized
if __name__.startswith('casatool'):

    # log some information
    from casatools import logsink
    logger = logsink(logfile)
    logger.post('python version %s' % sys.version, 'INFO')

    # make parent folder (ie .casa) if necessary
    if ('/' in rundata) and (rundata.rindex('/') > 0) and (not os.path.exists(rundata[:rundata.rindex('/')])):
        os.system('mkdir %s' % rundata[:rundata.rindex('/')])

    # update the IERS measures data if necessary
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

