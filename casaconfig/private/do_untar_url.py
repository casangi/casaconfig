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

def do_untar_url(dataURL, tarfile_name, path, extraction_filter=None, verbose_str=None, logger=None):
    """
    Treat the dataURL as the location of a probably compressed tar file
    with the given name and extract the contents into path.

    An extraction_filter can be supplied. See the documentation for the
    tarfile module for more details. If not suppled the standard
    'data_filter" extraction filter provided by the tarfile module is
    used. 

    If verbose_str is a non-empty string then this routine prints out
    a line showing the path that the contents are being downloaded to
    and the size of tar file. The verbose_str is used as the start of
    that output line.

    If logger is not None and verbose_str is a non-empty string then
    that output is also sent to logger, which should be an instance
    of the casalogger.

    If the location of the tarfile involves a redirect (e.g. go.nrao.edu
    for casarundata) then the part that is redirected should go 
    into dataURL. That is used first to get the true location that, when
    tarfile_name is added on to it, can be used as the full path to the
    tarfile.

    This routine is for internal use and is used by measures_updpate
    and do_pull_data.

    Parameters
       - dataURL (str) - The location where the tarfile_name is found. 
       - tarfile_name (str) - The name of the tarfile at dataURL to use.
       - path (str) - Folder path to place the tarball contents.
       - extraction_filter - An extraction_filter to use. See the tarfile module for more details. Defaults to "data_filter" if None.
       - verbose_str (str) - A string to prepend to the start of an information output on the location being populated (path) and the size of the tar file. If empty or None this routine does not print anything.
       - logger (casatools.logsink) - Instance of the casalogger to use for writing messages (verbose_str is set). If None then any output is only printed, not logged.

    Returns
       None
    """
    import os
    import sys

    import tarfile
    import ssl
    import urllib.request
    import certifi

    context = ssl.create_default_context(cafile=certifi.where())

    # this is needed to first resolve any redirect, e.g. go.nrao.edu, to find the true data URL
    targetURLroot = urllib.request.urlopen(dataURL, context=context).url
    targetURL = os.path.join(targetURLroot, tarfile_name)

    verboseOutput = isinstance(verbose_str,str) and len(verbose_str)>0

    with urllib.request.urlopen(targetURL, context=context, timeout=400) as tstream, tarfile.open(fileobj=tstream, mode='r|*') as tar :
        if verboseOutput:
            l = int(tstream.headers.get('content-length', 0))
            sizeString = "unknown size"
            if (l>0): sizeString = ("%.0fM" % (l/(1024*1024)))
            # use print directly to make use of the end argument
            print('%s %s (%s) ... ' % (verbose_str,path,sizeString), file = sys.stdout, end="" )
            sys.stdout.flush()
            # also log it
            if logger is not None: logger.post('downloading casarundata contents to %s ...' % path, 'INFO')

        if extraction_filter is None:
            # use the 'data_filter" if available, reverts to previous 'fully trusted' behavior if not available
            tar.extraction_filter = getattr(tarfile, 'data_filter', (lambda member, path: member))
        else:
            # use provided custom filter
            # measures_update uses this to provide a filter that excludes certain files
            tar.extraction_filter = extraction_filter
            
        tar.extractall(path=path)
        tar.close()

    if verboseOutput:
        print("done", file=sys.stdout)
        sys.stdout.flush()
