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
"""
this module will be included in the api
"""

def data_available():
    """
    List available casarundata versions on CASA server at https://go.nrao.edu/casarundata

    This returns a list of the casarundata versions available on the CASA
    server. The version parameter of data_update must be one
    of the values in that list if set (otherwise the most recent version
    in this list is used).

    A casarundata version is the filename of the tarball and look 
    like "casarundata.x.y.z.tar.*" (different compressions may be used by CASA without
    changing casaconfig functions that use those tarballs). The full filename is
    the casarundata version expected in casaconfig functions.

    Parameters
       None
    
    Returns
       list - version names returned as list of strings

    """

    import html.parser
    import urllib.request
    import ssl
    import certifi
    
    class LinkParser(html.parser.HTMLParser):
        def reset(self):
            super().reset()
            self.rundataList = []

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for (name, value) in attrs:
                    # only care if this is an href and the value starts with
                    # casarundata and has '.tar.' somewhere later and does not end in .md5
                    if name == 'href' and (value.startswith('casarundata') and (value.rfind('.tar')>11) and (value[-4:] != '.md5')):
                        # only add it to the list if it's not already there
                        if (value not in self.rundataList):
                            self.rundataList.append(value)

    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen('https://go.nrao.edu/casarundata/', context=context, timeout=400) as urlstream:
            parser = LinkParser()
            encoding = urlstream.headers.get_content_charset() or 'UTF-8'
            for line in urlstream:
                parser.feed(line.decode(encoding))

        # return the sorted list, earliest versions are first, newest is last
        return sorted(parser.rundataList)
    
    except Exception as exc:
        print("ERROR! : unexpected exception while getting list of available casarundata versions")
        print("ERROR! : %s" % exc)

    # nothing to return if it got here, must have been an exception
    return []

    
