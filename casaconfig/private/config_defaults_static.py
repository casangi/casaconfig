# search path for measurement sets and images to load, when empty then [measurespath] is used
datapath = [ ]

# location of geodetic and ephemera data, default path for casaconfig data functions
measurespath = "~/.casa/data"

# automatically update measures data if not current (measurespath must be owned by the user)
# when data_auto_update is True then measures_auto_update MUST also be True
measures_auto_update = True

# automatically update casarundata and measures data if not current (measurespath must be owned by the user)
data_auto_update = True

# location of the optional user's startup.py
startupfile = '~/.casa/startup.py'

# location of the cachedir
cachedir = '~/.casa'

# log file path/name
logfile='casa-%s.log' % _time.strftime("%Y%m%d-%H%M%S", _time.gmtime())

# do not create a log file when True, If True, then any logfile value is ignored and there is no log file
nologfile = False

# print log output to terminal when True (in addition to any logfile and CASA logger)
log2term = False

# do not start the CASA logger when True
nologger = False

# avoid starting GUI tools when True. If True then the CASA logger is not started even if nologger is False
nogui = False

# the IPython prompt color scheme. Must be one of "Neutral", "NoColor", "Linux" or "LightBG", default "Neutral"
colors = "Neutral"

# startup without a graphical backend if True
agg = False

# attempt to load the pipeline modules and set other options appropriate for pipeline use if True
pipeline = False

# create and use an IPython log using the iplogfile path
iplog = False

# the IPython log file path name to be used when iplog is True
iplogfile='ipython-%s.log' % _time.strftime("%Y%m%d-%H%M%S", _time.gmtime())

# allow anonymous usage reporting
telemetry_enabled = True

# location to place telemetry data prior to reporting
telemetry_log_directory = '~/.casa/telemetry'

# maximum size of telemetry recording
telemetry_log_limit = 20480

# telemetry recording size that triggers a report
telemetry_log_size_interval = 60

# telemetry recording report frequency
telemetry_submit_interval = 604800

# allow anonymous crash reporting
crashreporter_enabled = True

# include the user's local site-packages in the python path if True. May conflict with CASA modules
user_site = False
