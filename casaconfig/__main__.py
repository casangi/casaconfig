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
                     help="invokes data_update then measures_update to update measurespath to the latest casarundata and measures data")
parser.add_argument( "--reference-testing", action='store_const', const=True, dest='referencetesting', default=False,
                     help="set measurespath to the casarundata when this version of casa was produced, used for testing purposes")
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
        # do pull_update first when requested
        if flags.pulldata:
            print("pull_data using path=%s" % flags.measurespath)
            casaconfig.pull_data(flags.measurespath)
        # then data_update
        # if this follows a pull_data then the casarundata will be up to date and this will do nothing
        if flags.dataupdate:
            print("data_update using path=%s" % flags.measurespath)
            casaconfig.data_update(flags.measurespath)
        # then measures_update
        if flags.measuresupdate:
            print("measures_update using path=%s" % flags.measurespath)
            casaconfig.measures_update(flags.measurespath)
        # then updateall
        # if this follows other update options then this may do nothing
        if flags.updateall:
            print("data_update then measures_update using path=%s" % flags.measurespath)
            casaconfig.data_update(flags.measurespath)
            casaconfig.measures_update(flags.measurespath)
            
sys.exit(0)
