import unittest
import os, shutil, stat, sys, subprocess, time
from datetime import date, timedelta
import site
sitepackages = site.getsitepackages()[0]

import casaconfig

class casaconfig_test(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(os.path.expanduser("~/.casa/config.py")):
            os.replace(os.path.expanduser("~/.casa/config.py"), os.path.expanduser("~/.casa/config.py.user"))

        self.test_configpath =  os.path.join(os.path.expanduser("~/.casa/"),"config.py")
        self.test_siteconfigpath = os.path.join(os.getcwd(),'testsiteconfig.py')

        # testmeasures is used for measures-only tests
        # testrundata is used for full data install tests (at least casarundata is installed, which includes measures)
        # emptymeasures is used to test failure modes

        self.testMeasPath = os.path.join(os.getcwd(),'testmeasures')
        self.testRundataPath = os.path.join(os.getcwd(),'testrundata')
        self.emptyPath = os.path.join(os.getcwd(), 'emptymeasures')

        # this is set when needed and used if set, only query available versions once
        self.meas_avail = None

        # just in case something has left them populated
        self.rmTestDirs()

    def tearDown(self):
        for f in [self.test_configpath, self.test_siteconfigpath]:
            if os.path.isfile(f):
                os.remove(f)

        self.rmTestDirs();

        if os.path.isfile(os.path.expanduser("~/.casa/config.py.user")):
            os.replace(os.path.expanduser("~/.casa/config.py.user"), os.path.expanduser("~/.casa/config.py"))

    def rmTestDirs(self):
        if os.path.exists(self.testMeasPath):
            shutil.rmtree(self.testMeasPath)

        if os.path.exists(self.testRundataPath):
            shutil.rmtree(self.testRundataPath)

        if os.path.exists(self.emptyPath):
            shutil.rmtree(self.emptyPath)

    def get_meas_avail(self) :
        # this caches the list of available measures so measures_available() should only be called once for use by all tests
        if self.meas_avail is None:
            self.meas_avail = casaconfig.measures_available()
        return self.meas_avail

    def populate_testmeasures(self):
        # ensures that there's some casaconfig populated measures at self.testMeasPath
        # if there's a known version there it leave it as is
        # if the data info is None then it populates it with the most recent measures and extracts the observatory table
        # the data info version can not be illegal or unknown (something unexpected is already there)
        # this function works as a test, but it happens on demand in an attempt to limit the calls to update_measures
        
        dataInfo = casaconfig.get_data_info(self.testMeasPath, type='measures')
        if dataInfo is not None:
            version = dataInfo['version']
            self.assertTrue(not (version=="unknown" or version=="illegal"), "unexpected measures version in populate_testmeasures at %s : %s" % (self.testMeasPath,version))

            # it seems to be a valid measures installation, leave as is
            return

        # install the most recent available
        # since this is new measures install at path it needs to extract the Observatory table, which requires force to be True
        measVers = self.get_meas_avail()[-1]
        casaconfig.measures_update(self.testMeasPath, version=measVers, force=True, use_astron_obs_table=True)

        # check version (this makes this function a test, but it's used as needed elsewhere)
        dataInfo = casaconfig.get_data_info(self.testMeasPath, type='measures')
        self.assertTrue(dataInfo['version']==measVers,"unexpected version installed by populate_testmeasures at %s : %s != %s" % (self.testMeasPath, dataInfo['version'], measVers))

    def populate_testrundata(self):
        # ensures that there's some casaconfig populated casarundata at self.testMeasPath
        # if there's a known version there it leave it as is
        # if the data info is None then it populates it with the most recent casarundata
        # the data info version can not be illegal or unknown (something unexpected is already there)
        # this function works as a test, but it happens on demand in an attempt to limit the calls to pull_data
        
        dataInfo = casaconfig.get_data_info(self.testRundataPath, type='casarundata')
        if dataInfo is not None:
            version = dataInfo['version']
            self.assertTrue(not (version=="unknown" or version=="illegal"), "unexpected casarundata version in populate_testrundata at %s : %s" % (self.testRundataPath,version))

            # it seems to be a valid casarundata installation, leave as is
            return

        # install the most recent available
        # this query is cheap, don't cache it
        rundataVers = casaconfig.data_available()[-1]
        casaconfig.pull_data(self.testRundataPath, version=rundataVers)

        # check version (this makes this function a test, but it's used as needed elsewhere)
        dataInfo = casaconfig.get_data_info(self.testRundataPath, type='casarundata')
        self.assertTrue(dataInfo['version']==rundataVers, "unexpected version installed by populate_testrundata at %s : %s != %s" % (self.testRundataPath, dataInfo['version'], rundataVers))

    def test_file_exists(self):
        '''Test Default config.py exists in casaconfig module'''
        self.assertTrue(os.path.isfile('{}/casaconfig/config.py'.format(sitepackages)))

    @unittest.skipIf(not os.path.exists(os.path.join(sitepackages,'casatools')), "casatools not found")
    def test_import_casatools_bad_measurespath(self):
        '''Test that import casatools will return ImportError with measurespath set to an empty directory that cannot be written to'''
        # Due to casatools / casaconfig caching, run the import of casatools and read stdout/stderr for ImportError
        # after first creating an empty measurespath directory with the write permissions turned off
        # and then creating a test config file using the path to that directory as measurespath

        if (not os.path.exists(self.emptyPath)):
            os.mkdir(self.emptyPath)
            
        # the current permissions
        pstat = stat.S_IMODE(os.stat(self.emptyPath).st_mode)
        # a bitmask that's the opposite of all of the write permission bits
        no_write = ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
        # remove the write permissions
        pstat = pstat & no_write
        os.chmod(self.emptyPath,pstat)

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write("measurespath='%s'\n" % self.emptyPath)
        f.close()
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()
        print("test_import_casatools_bad_measurespath")
        print(str(output))
        ref = True if "NotWritable" in str(output) else False
        self.assertTrue(ref, "NotWritable Not Found")

    def test_casaconfig_measures_available(self):
        '''Test That Today or Yesterday measures data is returned'''

        today = date.today()
        yesterday = today - timedelta(days=1)
        measuresdata_today = "WSRT_Measures_{}-160001.ztar".format(today.strftime("%Y%m%d"))
        measuresdata_yesterday= "WSRT_Measures_{}-160001.ztar".format(yesterday.strftime("%Y%m%d"))

        self.assertTrue(any(elem in self.get_meas_avail() for elem in [measuresdata_today, measuresdata_yesterday]))

    def test_casaconfig_measures_update(self):
        '''Test downgrade to upgrade measures data to location'''
        
        # make sure something is already there
        self.populate_testmeasures()
        versInstalled = casaconfig.get_data_info(path=self.testMeasPath, type='measures')['version']

        # find the most recent version not installed at testPath
        vers = None
        for vers in reversed(self.get_meas_avail()):
            if vers != versInstalled:
                break

        # install that one
        casaconfig.measures_update(self.testMeasPath, version=vers, logger=None)

        # make sure that was just installed
        newVers = casaconfig.get_data_info(path=self.testMeasPath, type='measures')['version']

        self.assertTrue(newVers == vers)

    @unittest.skipIf(not os.path.exists(os.path.join(sitepackages,'casatools')), "casatools not found")
    def test_read_measurespath_from_user_config(self):
        '''Test casaconfig downloads specific measures data to location and casatools reads that data location'''

        # this requires that there be the full casarundata already installed
        self.populate_testrundata()

        # use the most recent version
        vers = self.get_meas_avail()[-1]

        # if that version is the one already installed then go back to the previous measures version
        if (casaconfig.get_data_info(path=self.testRundataPath, type='measures')['version'] == vers) :
            vers = self.get_meas_avail()[-2]

        # start a fresh process with a test config file setting measurespath to the testrundata
        # directory; in that process, import casaconfig and update the measures data to vers
        # then import casatools and verify that utils measurespath agrees with casaconfig measurespath

        fc = open(self.test_configpath,"w")
        fc.write("# Test Config File\n")
        fc.write('measurespath = "{}"\n'.format(self.testRundataPath))
        fc.close()

        # the test script to execute via the "-c" option in the process
        # the string is enclosed in double quotes when used, so only single quotes should appear within the string
        test_string = ''
        test_string += "import casaconfig; "
        test_string += "casaconfig.measures_update(path='{}',version='{}',force=False,logger=None); ".format(self.testRundataPath,vers)
        test_string += "import casatools; "
        test_string += "assert('{}' == casatools.utils.utils().measurespath())".format(self.testRundataPath)

        proc = subprocess.Popen('{} -c "{}"'.format(sys.executable,test_string), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        ref = False if "AssertionError" in str(output) else True
        print("test_read_measurespath_from_user_config")
        print(str(output))
        self.assertTrue(ref, "AssertionError seen in output : expected utils().measurespath() was not seen")

        # final check that the expected version is now installed
        installedVers = casaconfig.get_data_info(path=self.testRundataPath,type='measures')['version']
        self.assertTrue(installedVers == vers, "expected version was not installed : %s != %s" % (installedVers, vers))
        
    @unittest.skipIf(not os.path.exists(os.path.join(sitepackages,'casatools')), "casatools not found")
    def test_auto_update_measures(self):
        '''Test Automatic Measures Updates to measurespath'''

        # this requires that there be the full casarundata already installed
        self.populate_testrundata()

        # make sure the installed version is not the most recent one
        latestVers = self.get_meas_avail()[-1]
        versInstalled = casaconfig.get_data_info(self.testRundataPath,type='measures')['version']
        if (versInstalled == latestVers) :
            # force an install to the version before the most recent
            casaconfig.measures_update(self.testRundataPath, version=self.get_meas_avail()[-2], force=True, logger=None)
            # double check that that worked
            versInstalled = casaconfig.get_data_info(self.testRundataPath,type='measures')['version']
            self.assertTrue(versInstalled == self.get_meas_avail()[-2],"downgrade of measures to %s failed at %s, installed is %s" % (self.get_meas_avail()[-2], self.testRundataPath, versInstalled))
            
        # make sure the timestamp the measures readme files is more than 24 hrs old
        measuresReadmePath = os.path.join(self.testRundataPath,'geodetic/readme.txt')
        olderTime = time.time()-2.*24*60*60
        os.utime(measuresReadmePath,(olderTime,olderTime))

        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write('measurespath = "{}"\n'.format(self.testRundataPath))
        f.write('measures_auto_update = True\n')
        f.write('data_auto_update = False\n')
        f.close()

        # start a new casatools, which should update the measures to the most recent version
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        # output should contain the latest version string
        ref = self.get_meas_avail()[-1] in str(output)
        print("test_auto_update_measures")
        print(str(output))
        self.assertTrue(ref, "Update Failed")

    @unittest.skipIf(not os.path.exists(os.path.join(sitepackages,'casatools')), "casatools not found")
    def test_auto_install_data(self):
        '''Test auto install of all data to measurespath on casatools startup'''

        # make sure that testrundata does not exist
        if os.path.exists(self.testRundataPath):
            shutil.rmtree(self.testRundataPath)

        # set the user's config file to use testRundataPath as measurespath, with auto updates on
        fc = open(self.test_configpath,"w")
        fc.write("# Test Config File\n")
        fc.write('measurespath = "{}"\n'.format(self.testRundataPath))
        fc.write('data_auto_update = True\n')
        fc.write('measures_auto_update = True\n')
        fc.close()

        # it should fail if this attempt is made when that location does not exist
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()
        ref = True if "AutoUpdatesNotAllowed" in str(output) else False
        print("test_auto_install_data, 1")
        print(str(output))
        self.assertTrue(ref, "AutoUpdatesNotAllowed not found")

        # create testRundataPath and try again
        os.mkdir(self.testRundataPath)
        proc = subprocess.Popen('{} -c "import casatools"'.format(sys.executable), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()
        print("test_auto_install_data, 2")
        print(str(output))
        ref = True if "ImportError" not in str(output) else False
        self.assertTrue(ref, "ImportError Found")

        # final check that the expected versions were found
        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        expectedDataVersion = casaconfig.data_available()[-1]
        expectedMeasVersion = self.get_meas_avail()[-1]
        ref = (dataInfo['casarundata']['version'] == expectedDataVersion) and (dataInfo['measures']['version'] == expectedMeasVersion)
        print("test_auto_install_data, 3")
        print(str(output))
        self.assertTrue(ref, "Expected versions not installed")

    def test_daily_update(self):
        '''test that updates do not happen if the installed data is less than 1 day old and do happen when they are older'''

        # start with an empty testrundata
        if os.path.exists(self.testRundataPath):
            shutil.rmtree(self.testRundataPath)

        # populate it with an older version of casarundata
        oldVersion = casaconfig.data_available()[-2]
        casaconfig.pull_data(self.testRundataPath, version=oldVersion)

        # get the versions installed
        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        rundataVers = dataInfo['casarundata']['version']
        rundataAge = dataInfo['casarundata']['age']
        measVers = dataInfo['measures']['version']
        measAge = dataInfo['measures']['age']


        self.assertTrue(oldVersion == rundataVers, "old version was not installed as expected")
        self.assertTrue((rundataAge < 1.0) and (measAge < 1.0), "recent installed old versions do not have the expected recent age")

        # updates should do nothing
        casaconfig.data_update(self.testRundataPath)
        casaconfig.measures_update(self.testRundataPath)

        # versions should be unchanged
        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        checkRundataVers = dataInfo['casarundata']['version']
        checkMeasVers = dataInfo['measures']['version']

        self.assertTrue((checkRundataVers == rundataVers) and (checkMeasVers == measVers), "unexpected update of recently installed data")

        # back date measures and try to update
        measuresReadmePath = os.path.join(self.testRundataPath,'geodetic/readme.txt')
        olderTime = time.time()-2.*24*60*60
        os.utime(measuresReadmePath,(olderTime,olderTime))

        # measures should update, rundata should not
        casaconfig.data_update(self.testRundataPath)
        casaconfig.measures_update(self.testRundataPath)

        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        checkRundataVers = dataInfo['casarundata']['version']
        checkRundataAge = dataInfo['casarundata']['age']
        checkMeasVers = dataInfo['measures']['version']
        checkMeasAge = dataInfo['measures']['age']

        self.assertTrue((checkRundataVers == rundataVers) and (checkMeasVers != measVers), "versions are not as expected after a measures update")

        # backdate the rundata
        rundataReadmePath = os.path.join(self.testRundataPath,'readme.txt')
        os.utime(rundataReadmePath,(olderTime,olderTime))

        # data should update now
        casaconfig.data_update(self.testRundataPath)

        # what's the age now
        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        casaconfig.measures_update(self.testRundataPath)

        dataInfo = casaconfig.get_data_info(self.testRundataPath)
        checkRundataVers = dataInfo['casarundata']['version']
        checkMeasVers = dataInfo['measures']['version']

        # IF a new measures tarball was made available while this test was running then the updated measure here may be one more than the previous
        # update, so long as this is the most recent measures this test is OK
        expectedMeasVers = casaconfig.measures_available()[-1]
        self.assertTrue((checkRundataVers != rundataVers) and (checkMeasVers == expectedMeasVers), "versions are not as expected after a measures update")

    def do_config_check(self, expectedDict, noconfig, nositeconfig):
        '''Launch a separate python to load the config files, using --noconfig --nositeconfig as requested, the expectedDict contains expected values'''

        # the test script produces a dictionary of key,value where the keys are
        # loaded, failed, measurespath, measures_auto_update, and data_auto_update
        # all of the values are strings
        # loaded and failed are len(load_success()) and len(load_failure)
        # measurespath, measures_auto_update, data_auto_update are those values

        # returns a non-empty string if any of the expected values aren't found in the parsed output of from python subprocess
        
        # used by test_config_import

        msgs = ""
        
        # test script to execute via the "-c" option in the process
        # the string is enclosed in double quotes when used, so only single quotes should appear within the string
        test_string = ''
        test_string += "from casaconfig import config; "
        test_string += "print('failures :%s ' % config.load_failure()); "
        test_string += "print('loaded : %s' % len(config.load_success())); "
        test_string += "print('failed : %s' % len(config.load_failure())); "
        test_string += "print('measurespath : %s' % config.measurespath); "
        test_string += "print('measures_auto_update : %s' % config.measures_auto_update); "
        test_string += "print('data_auto_update : %s' % config.data_auto_update); "

        args = ""
        if noconfig:
            args += "--noconfig "
        if nositeconfig:
            args += "--nositeconfig "

        proc = subprocess.Popen('{} -c "{}" {}'.format(sys.executable,test_string,args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (output, _) = proc.communicate()

        p_status = proc.wait()

        resultsDict = {}
        for l in output.decode('utf-8').splitlines():
            parts = l.split(":")
            if (len(parts) != 2): continue

            resultsDict[parts[0].strip()] = parts[1].strip()

        for k in expectedDict:
            if k not in resultsDict:
                msgs += 'expected result for "{}" not found; '.format(k)
            else:
                if expectedDict[k] != resultsDict[k]:
                    msgs += 'unexpected result for "{}"; '.format(k)
        return msgs
        

    def test_config_import(self):
        '''Tests of the config import'''

        # the user's config file
        f = open(self.test_configpath,"w")
        f.write("# Test Config File\n")
        f.write('measurespath = "{}"\n'.format(self.testRundataPath))
        f.close()

        # the test site config file
        f = open(self.test_siteconfigpath,"w")
        f.write("#Test Siteconfig File\n")
        f.write('measurespath = "/path/doesnot/exist"\n')
        f.write('measures_auto_update = False\n')
        f.write('data_auto_update = False\n')
        f.close()


        # set the casasiteconfig env value
        os.environ['CASASITECONFIG'] = self.test_siteconfigpath

        expectedDict = {"loaded":"3",
                        "failed":"0",
                        "measurespath":self.testRundataPath,
                        "measures_auto_update":"False",
                        "data_auto_update":"False"}

        # test with both, 2 files loaded, no errors, user's measurespath, site's auto update values

        msgs = self.do_config_check(expectedDict, noconfig=False, nositeconfig=False)
        self.assertTrue(len(msgs)==0, "failed : config import with both user and site config files : " + msgs)

        # test with just the defaults
        
        expectedDict["loaded"] = "1"
        expectedDict["measurespath"] = os.path.abspath(os.path.expanduser('~/.casa/data'))
        expectedDict["measures_auto_update"] = "True"
        expectedDict["data_auto_update"] = "True"
        msgs = self.do_config_check(expectedDict, noconfig=True, nositeconfig=True)
        self.assertTrue(len(msgs)==0, "failed : config import of only defaults : " + msgs)

        # test with user + defaults, no site
        expectedDict["loaded"] = "2"
        expectedDict["measurespath"] = self.testRundataPath
        msgs = self.do_config_check(expectedDict, noconfig=False, nositeconfig=True)
        self.assertTrue(len(msgs)==0, "failed : config import ignoring site : " + msgs)

        # test with an error in the site config, should report the error and move on, leaving just the user + default expected values
        
        f = open(self.test_siteconfigpath,"w")
        f.write("#Test Siteconfig File with error\n")
        # the value whatever does not exist
        f.write('measurespath = whatever\n')
        f.write('measures_auto_update = False\n')
        f.write('data_auto_update = False\n')
        f.close()

        # expect 1 failure, with the user+defaults being the final values
        expectedDict["failed"] = "1"
        
        msgs = self.do_config_check(expectedDict, noconfig=False, nositeconfig=False)
        self.assertTrue(len(msgs)==0, "failed : config import with error in site : " + msgs)

        # unset CASASITECONFIG to ignore the site config file and try again, the site config should not be seen
        os.environ.pop('CASASITECONFIG')

        # the failure is now gone
        expectedDict["failed"] = "0"
        
        msgs = self.do_config_check(expectedDict, noconfig=False, nositeconfig=False)
        self.assertTrue(len(msgs)==0, "failed : config import with CASASITECONFIG unset : " + msgs)

            
if __name__ == '__main__':

    unittest.main()
