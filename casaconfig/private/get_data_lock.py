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

def get_data_lock(path, fn_name):
    """
    Get and initialize and set the lock on 'data_update.log' in path.

    If path does not already exist or the lock file is not empty then a lock
    is not set then a BadLock exception is raised.

    When a lock is set the lock file will contain the user, hostname, pid,
    date, and time.

    The opened file descriptor holding the lock is returned.

    The caller is responsible for closing the returned file descriptor to release the
    lock. The lock file should be truncated if everything went as expected.

    This function is intended for internal casaconfig use.

    Parameters
       - path (str) - The location where 'data_update.log' is to be found.
       - fn_name (str) - A string giving the name of the calling function to be recorded in the lock file.

    Returns:
       - the open file descriptor holding the lock. Close this file descriptor to release the lock.

    Raises:
        - casaconfig.BadLock - raised when the path to the lock file does not exist or the lock file is not empty as found
        - Exception - an unexpected exception was seen while writing the lock information to the file

    """

    import fcntl
    import os
    import getpass
    from datetime import datetime

    from casaconfig import BadLock

    if not os.path.exists(path):
        raise BadLock("path to contain lock file does not exist : %s" % path)

    lock_path = os.path.join(path, 'data_update.lock')
    lock_exists = os.path.exists(lock_path)

    # open and lock the lock file - don't truncate the lock file here if it already exists, wait until it's locked
    mode = 'r+' if os.path.exists(lock_path) else 'w'
    lock_fd = open(lock_path, mode)
    fcntl.lockf(lock_fd, fcntl.LOCK_EX)

    # see if the lock file is empty
    if (lock_exists):
        lockLines = lock_fd.readlines()
        if (len(lockLines) > 0) and (len(lockLines[0]) > 0):
            # not empty
            lock_fd.close()
            raise BadLock("lock file is not empty : %s" % lock_path)

    # write the lock information, the seek and truncate are probably not necessary
    try:
        lock_fd.seek(0)
        lock_fd.truncate(0)
        lock_fd.write("locked using %s by %s on %s : pid = %s at %s" % (fn_name, getpass.getuser(), os.uname().nodename, os.getpid(), datetime.today().strftime('%Y-%m-%d:%H:%M:%S')))
        lock_fd.flush()
    except Exception as exc:
        print("ERROR! Unexpected failure in writing lock information to lock file %s" % lock_path)
        print("ERROR! Called by function : %s" % fn_name)
        print("ERROR! : %s" % exc)
        lock_fd.close()
        # reraise the exception - this shouldn't happen
        raise exc

    return lock_fd
   
