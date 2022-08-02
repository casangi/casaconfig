import os
import sys
from contextlib import contextmanager

def _fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd

@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stdout

    stdout_fd = _fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied:
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(_fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied

@contextmanager
def all_redirected(to=os.devnull):
    stdout = sys.stdout
    stderr = sys.stderr

    stdout_fd = _fileno(stdout)
    stderr_fd = _fileno(stderr)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as out_copied, os.fdopen(os.dup(stderr_fd), 'wb') as err_copied:
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(_fileno(to), stdout_fd)  # $ exec >&to
            os.dup2(_fileno(to), stderr_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
                os.dup2(to_file.fileno(), stderr_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(out_copied.fileno(), stdout_fd)  # $ exec >&copied
            os.dup2(err_copied.fileno(), stderr_fd)  # $ exec >&copied

@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target # replace sys.stdout
    try:
        yield new_target # run some code with the replaced stdout
    finally:
        sys.stdout = old_target # restore to the previous value

def merged_stderr_stdout():  # $ exec 2>&1
    return stdout_redirected(to=sys.stdout, stdout=sys.stderr)

@contextmanager
def no_redirect( ):
    yield None
