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

def measures_available():
    """
    List available measures versions on ASTRON server at https://www.astron.nl/iers/

    This returns a list of the measures versions available on the ASTRON
    server. The version parameter of measures_update must be one
    of the values in that list if set (otherwise the most recent version
    in this list is used).

    Parameters
       None
    
    Returns
       list - version names returned as list of strings

    Raises
       - casaconfig.NoNetwork - Raised where there is no network seen, can not continue
       - casaconfig.RemoteError - Raised when there is an error fetching some remote content for some reason other than no network
       - Exception - Unexpected exception while getting list of available measures versions

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
        def reset(self):
            super().reset()
            self.rundataList = []

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for (name, value) in attrs:
                    # only care if this is an href and the value starts with
                    # WSRT_Measures and has 'tar' after character 15 to exclude the "WSRT_Measures.ztar" file
                    # without relying on the specific type of compression or nameing in  more detail than that
                    if name == 'href' and (value.startswith('WSRT_Measures') and (value.rfind('tar')>15)):
                        # only add it to the list if it's not already there
                        if (value not in self.rundataList):
                            self.rundataList.append(value)

    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen('https://www.astron.nl/iers', context=context, timeout=400) as urlstream:
            parser = LinkParser()
            encoding = urlstream.headers.get_content_charset() or 'UTF-8'
            for line in urlstream:
                parser.feed(line.decode(encoding))

        # return the sorted list, earliest versions are first, newest is last
        return sorted(parser.rundataList)

    except urllib.error.URLError as urlerr:
        raise RemoteError("Unable to retrieve list of available measures versions : " + str(urlerr)) from None
        
    except Exception as exc:
        msg = "Unexpected exception while getting list of available measures versions : " + str(exc)
        raise Exception(msg)

    # nothing to return if it got here, must have been an exception
    return []

    
