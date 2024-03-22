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

def do_pull_data(path, version, installed_files, currentVersion, currentDate, logger):
    """
    Pull the casarundata for the given version and install it in path, removing
    the installed files and updating the readme.txt file when done.

    This function is used by both pull_data and data_update when each has
    determind that the desired version should be installed. The calling function
    has already obtained the lock. No additional checking happens here. The
    calling function has already examined any existing readme file and used that
    to set the installed_files list as appropriate. 

    Parameters
       - path (str) - Folder path to place casadata contents.
       - version (str) - casadata version to retrieve.
       - installed_files (str list) - list of installed files from the version already installed. Set to an empty list if there is no previously installed version.
       - currentVersion (str) - from the readme file if it already exists, or an empty string if there is no previously installed version.
       - currentDate (str) - from the readme file if it already exists, or an empty string if there is no previously installed version.
       - logger (casatools.logsink) - Instance of the casalogger to use for writing messages. Messages are always written to the terminal. Set to None to skip writing messages to a logger.

    Returns
       None

    """

    import os
    import sys
    from datetime import datetime
    import ssl
    import urllib.request
    import certifi
    import tarfile
    import shutil

    from .print_log_messages import print_log_messages
    
    readme_path = os.path.join(path, 'readme.txt')

    if (installed_files is not None and len(installed_files) > 0):
        # remove the previously installed files
        # remove this readme file so it's not confusing if something goes wrong after this
        os.remove(readme_path)
        print_log_messages('Removing files using manifest from previous install of %s on %s' % (currentVersion, currentDate), logger)
        for relpath in installed_files:
            filepath = os.path.join(path,relpath)
            # don't say anything if filepath isn't found, remove it if it is found
            if os.path.exists(filepath) and os.path.isfile(filepath):
                os.remove(filepath)
        
        # remove any empty directories in path - this is recursive
        def remove_empty_dirs(dirpath):
            # look at all of the files in dirpath, for dirs, go down that recursively
            # if there's nothing there after the dirs have all been handled, remove it
            files = os.listdir(dirpath)
            not_dirs = []
            for f in os.listdir(dirpath):
                fpath = os.path.join(dirpath, f)
                if os.path.isdir(fpath):
                    remove_empty_dirs(fpath)
                else:
                    not_dirs.append(f)
            if len(not_dirs) == 0:
                if len(os.listdir(dirpath)) == 0:
                    os.rmdir(dirpath)
                    
        remove_empty_dirs(path)

    # okay, safe to install the requested version

    goURL = 'https://go.nrao.edu/casarundata'
    context = ssl.create_default_context(cafile=certifi.where())

    # need to first resolve the go.nrao.edu URL to find the actual data URL
    dataURLroot = urllib.request.urlopen(goURL, context=context).url
    dataURL = os.path.join(dataURLroot, version)
    
    with urllib.request.urlopen(dataURL, context=context, timeout=400) as tstream, tarfile.open(fileobj=tstream, mode='r|*') as tar :
        l = int(tstream.headers.get('content-length', 0))
        sizeString = "unknown size"
        if (l>0): sizeString = ("%.0fM" % (l/(1024*1024)))
        # use print directly to make use of the end argument
        print('downloading casarundata contents to %s (%s) ... ' % (path,sizeString), file = sys.stdout, end="" )
        sys.stdout.flush()
        # also log it
        if logger is not None: logger.post('downloading casarundata contents to %s ...' % path, 'INFO')
        # use the 'data' filter if available, revert to previous 'fully_trusted' behavior of not available
        tar.extraction_filter = getattr(tarfile, 'data_filter', (lambda member, path: member))
        tar.extractall(path=path)
        
    print("done", file=sys.stdout)
        
    # the tarball has been extracted to path/version
    # get the instaled files of files to be written to the readme file
    versdir = os.path.join(path,version[:version.index('.tar')])
    installed_files = []
    wgen = os.walk(versdir)
    for (dirpath, dirnames, filenames) in wgen:
        for f in filenames:
            installed_files.append(os.path.relpath(os.path.join(dirpath,f),versdir))
                
    # move everything in version up a level to path
    for f in os.listdir(versdir):
        srcPath = os.path.join(versdir,f)
        if os.path.isdir(srcPath):
            # directories are first copied, then removed
            # existing directories are reused, existing files are overwritten
            # things in path that do not exist in srcPath are not changed
            shutil.copytree(srcPath,os.path.join(path,f),dirs_exist_ok=True)
            shutil.rmtree(srcPath)
        else:
            # assume it's a simple file, these can be moved directly, overwriting anything already there
            os.rename(srcPath,os.path.join(path,f))
                        
    # safe to remove versdir, it would be a surprise if it's not empty
    os.rmdir(versdir)
    # update the readme.txt file
    with open(readme_path,'w') as fid:
        fid.write("# casarundata populated by casaconfig.pull_data\nversion : %s\ndate : %s" % (version, datetime.today().strftime('%Y-%m-%d')))
        fid.write("\n#\n# manifest")
        for f in installed_files:
            fid.write("\n%s" % f)

    print_log_messages('casarundata installed %s at %s' % (version, path), logger)
