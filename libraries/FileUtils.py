import fnmatch
import os
import time
from pathlib import Path

from RPA.FileSystem import File, TimeoutException


def is_file_pdf_exist(download_dir):
    for file in os.listdir(download_dir):
        if fnmatch.fnmatch(file, '*.pdf'):
            return file
        else:
            "file not found"


def is_file_xml_exist(download_dir):
    for file in os.listdir(download_dir):
        if fnmatch.fnmatch(file, '*.xml'):
            return file
        else:
            "file not found"


def wait_file(path, condition, timeout):
    """Poll file with `condition` callback until it returns True,
    or timeout is reached.
    """
    path = Path(path)
    end_time = time.time() + float(timeout)
    while time.time() < end_time:
        if condition(path):
            return True
        time.sleep(0.1)
    return False


def wait_until_pdf_file_created(path, timeout=5.0):
    """Poll path until it exists, or raise exception if timeout
    is reached.

    :param path:    path to poll
    :param timeout: time in seconds until keyword fails
    """
    if not wait_file(path, lambda file: is_file_pdf_exist(file), timeout):
        raise TimeoutException("Path was not created within timeout")

    return File.from_path(path)


def wait_until_xml_file_created(path, timeout=5.0):
    """Poll path until it exists, or raise exception if timeout
    is reached.

    :param path:    path to poll
    :param timeout: time in seconds until keyword fails
    """
    if not wait_file(path, lambda file: is_file_pdf_exist(file), timeout):
        raise TimeoutException("Path was not created within timeout")

    return File.from_path(path)
