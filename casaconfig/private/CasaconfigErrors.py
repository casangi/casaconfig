# Copyright 2024 AUI, Inc. Washington DC, USA
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

class AutoUpdatesNotAllowed(Exception):
    """Raised when a path does not exist or is not owned by the user"""
    pass

class BadLock(Exception):
    """Raised when the lock file is not empty and a lock attempt was made"""
    pass

class BadReadme(Exception):
    """Raised when a readme.txt file does not contain the expected contents"""
    pass

class NoReadme(Exception):
    """Raised when the readme.txt file is not found at path (path also may not exist)"""

class RemoteError(Exception):
    """Raised when there is an error fetching some remote content"""
    pass

class NotWritable(Exception):
    """Raised when the path is not writable by the user"""

class UnsetMeasurespath(Exception):
    """Raised when a path argument is None"""
    pass
