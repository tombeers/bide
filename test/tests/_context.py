import os
import shutil



def _current_directory_path():
    return os.path.realpath(os.curdir)


def _temporary_directory_path():
    return os.path.join(_current_directory_path(), 'temporary')


def _temporary_subdirectory_path():
    return os.path.join(_temporary_directory_path(), 'directory')


def _make(path):
    os.makedirs(path)

    return path


def _make_temporary_directory():
    return _make(_temporary_directory_path())


def _make_temporary_subdirectory():
    return _make(_temporary_subdirectory_path())


def _remove(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def _remove_temporary_directory():
    return _remove(_temporary_directory_path())


def _remove_temporary_subdirectory():
    return _remove(_temporary_subdirectory_path())
