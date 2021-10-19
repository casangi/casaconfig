import time
import pkg_resources

if __name__ == 'casatoolrc':
    print('\ncasatool specific configuration\n')


datapath=[pkg_resources.resource_filename('casaconfig', '__data__/')]
rundata="~/.casadata"
logfile='casalog-%s.log' % time.strftime("%Y%m%d-%H",time.localtime())
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

