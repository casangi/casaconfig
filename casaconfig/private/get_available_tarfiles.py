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

def get_available_tarfiles(urlstr, startswith):
    """
    Returns a sorted list of all likely tarfiles found at the URL given by 
    urlstr that start with the string "startswith". 

    The file name must also contain "tar" anywhere after the startswith 
    string. File names that end in ".md5" are excluded from the returned list.

    This function does the work for measures_available and data_available.

    Parameters
       - urlstr (str) - The URL to be used when finding the files.
       - startswith (str) - Files that start with startswith are included in the returned list
    
    Returns
        list - the list of file names found at urlstring matching the criteria

    Raises
       - casaconfig.NoNetwork - Raised when there is no network seen, can not continue.
       - urllib.error.URLError - Raised when there is an error fetching some remote content for some reason other than no network.
       - Exception - Unexpected exception while getting the list of available tarfiles.
    """

    import html.parser
    import urllib.request
    import urllib.error
    import ssl
    import certifi

    from casaconfig import RemoteError
    from casaconfig import NoNetwork

    from .have_network import have_network

    if not have_network():
        raise NoNetwork("No network, can not find the list of available data.")
    
    class LinkParser(html.parser.HTMLParser):

        def __init__(self, startswith):
            self._startswith = startswith
            super().__init__()
            
        def reset(self):
            super().reset()
            self.rundataList = []

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for (name, value) in attrs:
                    # only care if this is an href and the value starts with
                    # startswith and has 'tar' after character 15 to exclude the "WSRT_Measures.ztar" file
                    # without relying on the specific type of compression or nameing in  more detail than that
                    if name == 'href' and (value.startswith(startswith) and (value.rfind('tar')>len(startswith)) and (value[-4:] != '.md5')):
                        # only add it to the list if it's not already there
                        if (value not in self.rundataList):
                            self.rundataList.append(value)

    # don't look for any exceptions here, this will raise urllib.error.URLError for most URL errors
    # other exceptions are unexpected but should be watched for upstream
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(urlstr, context=context, timeout=400) as urlstream:
        parser = LinkParser(startswith)
        encoding = urlstream.headers.get_content_charset() or 'UTF-8'
        for line in urlstream:
            parser.feed(line.decode(encoding))

    # return the sorted list, earliest versions are first, newest is last
    return sorted(parser.rundataList)

    # nothing to return if it got here, must have been an exception
    return []

    

    
    
