import os, time, pkg_resources

# list of paths where CASA should search for data subdirectories
datapath = [pkg_resources.resource_filename('casaconfig', '__data__/')]

# location of required runtime measures data, takes precedence over location(s) in datapath list
rundata = os.path.expanduser("~/.casa/measures")

# automatically populate the datapath[0] location if not already done
populate_data = True

# automatically update measures data if not current (rundata must be user-writable)
measures_update = True

# log file path/name
logfile='casalog_%s.log' % time.strftime("%Y-%m-%d", time.localtime())

# do not create a log file when True, If True, then any logfile value is ignored and there is no log file
nologfile = False

# print log output to terminal when True (in addition to any logfile and CASA logger)
log2term = False

# do not start the CASA logger when True
nologger = False

# avoid starting GUI tools when True. If True then the CASA logger is not started even if nologger is False
nogui = False

# the IPython prompt color scheme. Must be one of “Neutral”, “NoColor”, “Linux” or “LightBG”, default “Neutral”
# if an invalid color is given a warning message is printed and logged but CASA continues using the default color
colors = "LightBG"

# startup without a graphical backend if True
agg = False

# attempt to load the pipeline modules and set other options appropriate for pipeline use if True
# when pipeline is True then agg will be assumed to be true even if agg is set to False here or on the command line
pipeline = False

# create and use an IPython log in the current directory if True
iplog = True

# allow anonymous usage reporting
telemetry_enabled = True

# location to place telemetry data prior to reporting
telemetry_log_directory = os.path.expanduser("~/.casa/telemetry")

# maximum size of telemetry recording
telemetry_log_limit = 1650

# telemetry recording size that triggers a report
telemetry_log_size_interval = 30

# telemetry recording report frequency
telemetry_submit_interval = 20

# allow anonymous crash reporting
crashreporter_enabled = True

# include the user’s local site-packages in the python path if True. 
# normally these are excluded to avoid any conflicts with CASA modules
user_site = False

