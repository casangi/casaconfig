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

    If path does not already exist and the lock file is not empty then a lock
    is not set and the returned value is None.

    When a lock is set the lock file will contain the user, hostnames, pid,
    date, and time.

    The opened file descriptor holding the lock is returned.

    The caller is responsible for closing the returned file descriptor to release the
    lock. The lock file should be truncated if everything went as expected.

    This function is intended for internal casaconfig use.

    Parameters
       - path (str) - The location where 'data_update.log' is to be found.
       - fn_name (str) - A string giving the name of the calling function to be recorded in the lock file.
    Returns
       - the open file descriptor holding the lock. Close this file descriptor to release the lock. Returns None if path does not exist or the lock file is not empty.

    """

    import fcntl
    import os
    from datetime import datetime

    if not os.path.exists(path): return None

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
            return None

    # write the lock information, the seek and truncate are probably not necessary
    try:
        print("lock file fd obtained for %s" % lock_path)
        lock_fd.seek(0)
        print("seek")
        lock_fd.truncate(0)
        print("truncated")
        print("writing lock information")
        print("fn_name : %s" % fn_name)
        print("os.getlogin() : %s" % os.getlogin())
        print("os.uname().nodename : %s" % os.uname().nodename)
        print("os.getpid() : %s" % os.getpid())
        print("datetime.today : %s" % datetime.today().strftime('%Y-%m-%d:%H:%M:%S'))
        lock_fd.write("locked using %s by %s on %s : pid = %s at %s" % (fn_name, os.getlogin(), os.uname().nodename, os.getpid(), datetime.today().strftime('%Y-%m-%d:%H:%M:%S')))
        print("info written")
        lock_fd.flush()
        print("lock_fd flushed")
    except:
        import traceback
        traceback.print_exc()

    return lock_fd
   
