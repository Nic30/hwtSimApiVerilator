from contextlib import contextmanager
import fnmatch
import os
import shutil
import tempfile


@contextmanager
def working_directory(directory):
    owd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(owd)


@contextmanager
def tempdir(suffix=None, prefix=None, dir=None):
    dirpath = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    yield dirpath
    shutil.rmtree(dirpath)




def find_files(directory, pattern, recursive=True):
    """
    Find files by pattern in directory
    """
    if not os.path.isdir(directory):
        if os.path.exists(directory):
            raise IOError(directory + ' is not directory')
        else:
            raise IOError(directory + " does not exists")
    if recursive:
        for root, _, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename
    else:
        root = directory
        for basename in os.listdir(root):
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                if os.path.isfile(filename):
                    yield filename
