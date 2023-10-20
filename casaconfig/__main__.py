import sys
import os
from casaconfig.private.get_argparser import get_argparser

parser = get_argparser(add_help=True)

# get_argparser supplies configfile, noconfig, nositeconfig
# add measurespath, pull-data, data-update, measures-update, update-all, reference-testing, current-data

# measurespath will default to the value in config if not set here
parser.add_argument( "--measurespath", dest='measurespath', default=None,
                     help="location of casarundata")

parser.add_argument( "--pull-data", dest='pulldata', action='store_const', const=True, default=False,
                     help="invoke pull_data() to populate measurespath with latest casarundata")
parser.add_argument( "--data-update", dest='dataupdate', action='store_const', const=True, default=False,
                     help="invoke data_update() to update measurespath to the latest casarundata")
parser.add_argument( "--measures-update", dest='measuresupdate', action='store_const', const=True, default=False,
                     help="invoke measures_update() to update measurespath to the latest measures data")
parser.add_argument( "--update-all", dest='updateall', action='store_const', const=True, default=False,
                     help="invoke update_all() to populate (update) measurespath with the latest casarundata and measures data")
parser.add_argument( "--reference-testing", action='store_const', const=True, dest='referencetesting', default=False,
                     help="set measurespath to the casarundata when this version was produced, used for testing purposes")
parser.add_argument( "--current-data", dest='currentdata', action='store_const', const=True, default=False,
                     help="print out a summary of the current casarundata and measures data installed in measurespath and then exit")

# initialize the configuration to be used
flags,args = parser.parse_known_args(sys.argv)
from casaconfig import config

# import the casaconfig module
import casaconfig

# make sure measurespath reflects any command line value
if flags.measurespath is None:
    flags.measurespath = config.measurespath

# watch for measurespath of None, that likely means that casasiteconfig.py is in use and this has not been set. It can't be used then.
if flags.measurespath is None:
    print("measurespath has been set to None, likely in casasiteconfig.py.")
    print("Either provide a measurespath on the casaconfig command line or edit casasiteconfig.py or other a user config.py to set measurespath to a location.")
    sys.exit(1)

# do any expanduser and abspath
measurespath = os.path.abspath(os.path.expanduser(flags.measurespath))

if flags.currentdata:
    if not os.path.exists(measurespath) or not os.path.isdir(measurespath):
        print("No data installed at %s. The measurespath does not exist or is not a directory." % flags.measurespath)
    else:
        # casarundata
        datareadme = os.path.join(measurespath,'readme.txt')
        if not os.path.exists(datareadme):
            print("No casarundata installed in %s (missing readme.txt)." % flags.measurespath)
        else:
            try:
                with open(datareadme, 'r') as fid:
                    readme = fid.readlines()
                    currentVersion = readme[1].split(':')[1].strip()
                    currentDate = readme[2].split(':')[1].strip()
                    print('casarundata version %s installed on %s' % (currentVersion, currentDate))
                    if (len(readme)<4):
                        print('    casarundata appears to be too short, missing list of installed files, casarundata should be repopulated in %s' % flags.measurespath)
            except:
                print('There was a problem reading the casarundata readme.txt, casarundata should be repopulated in %s' % flags.measurespath)
                
        # measures
        measuresreadme = os.path.join(measurespath,'geodetic/readme.txt')
        if not os.path.exists(measuresreadme):
            print("No measures data installed in %s/geodetic (missing readme.txt)." % flags.measurespath)
        else:
            try:
                with open(measuresreadme, 'r') as fid:
                    readme = fid.readlines()
                    currentVersion = readme[1].split(':')[1].strip()
                    currentDate = readme[2].split(':')[1].strip()
                    print('measures version %s installed on %s' % (currentVersion, currentDate))
            except:
                print('There was a problem reading the measures readme.txt, measures should be repopulated in %s' % flags.measurespath)
 
    # ignore any other arguments

else:
    if flags.referencetesting:
        print("--reference-testing is not yet implemented, measurespath=%s" % flags.measurespath)
        # ignore any other arguments
        
    else:
        # the update options, update all does everything, no need to invoke anything else
        if flags.updateall:
            print("data_update then measures_update using path=%s" % flags.measurespath)
            casaconfig.update_all(flags.measurespath)
        else:
            # do any pull_update first
            if flags.pulldata:
                print("pull_data using path=%s" % flags.measurespath)
                casaconfig.pull_data(flags.measurespath)
            # then data_update, not necessary if pull_data just happened
            if flags.dataupdate and not flags.pulldata:
                print("data_update using path=%s" % flags.measurespath)
                casaconfig.data_update(flags.measurespath)
            # then measures_update
            if flags.measuresupdate:
                print("measures_update using path=%s" % flags.measurespath)
                casaconfig.measures_update(flags.measurespath)

sys.exit(0)
