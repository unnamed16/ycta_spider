__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2020/05/19'

import json
import os
import stat
from pathlib import Path
from typing import Any, AnyStr, List, Iterator, Tuple, Union, Set


ROOT_FOLDER = Path(__file__).parent.parent.resolve()
CONFIG_PATH = os.path.join(ROOT_FOLDER, 'config.json')



def read_config() -> dict:
    """
    Read the config file from the project's root\n
    :return: data from config.json specified for the trader project
    """
    return read_json(CONFIG_PATH)


def read_json(path: Union[str, Path]) -> Any:
    """
    Read a JSON file and return the extracted data\n
    :param path: string with the JSON file path
    :return: data from a JSON file. An empty string will be returned if an UnicodeDecodeError occurs while parsing
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except UnicodeDecodeError:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return data
        except UnicodeDecodeError:
            print("\033[93mWARNING: unable to decode file" + path + "\033[0m")
            return ""


def read_file(path: Union[str, Path]) -> AnyStr:
    """
    Read any file and return the extracted data as a string\n
    :param path: string with the file path
    :return: a string with data from file. It's an empty string if an UnicodeDecodeError occurs while parsing
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return data
    except UnicodeDecodeError:
        try:
            with open(path, 'r') as f:
                data = f.read()
            return data
        except UnicodeDecodeError:
            print("\033[93mWARNING: unable to decode file" + path + "\033[0m")
            return ""
        except MemoryError:
            print("\033[93mWARNING: not enough memory to read file" + path + "\033[0m")
            return ""
    except MemoryError:
        print("\033[93mWARNING: not enough memory to read file" + path + "\033[0m")
        return ""


def read_files(
        path: str,
        suffixes: Set[str] = None,
        skip_hidden_dirs: bool = True) -> Iterator[Tuple[str, AnyStr]]:
    """
    Read all the files with the given suffixes from the given directory and its subdirectories\n
    :param path: string with the path to the directory to search in
    :param suffixes: set of suffixes of files that should be obtained. All the files will be obtained if Null
    :param skip_hidden_dirs: if True - skips hidden directories, default = True
    :return: generator of file sub-path and its content pairs
    """
    for filename in browse_file_sub_paths(path, suffixes, skip_hidden_dirs=skip_hidden_dirs):
        yield filename, read_file(filename)


def browse_file_sub_paths(
        path: str,
        suffix_list: List[str] = None,
        skip_hidden_dirs: bool = True) -> Iterator[str]:
    """
    Browse for files with the given suffixes in the given directory and its subdirectories\n
    :param path: string with the path to the directory to search in
    :param suffix_list: list of valid suffixes. Any suffix is valid if the list is None
    :param skip_hidden_dirs: if True - skips hidden directories, default = True
    :return: file path strings generator
    """
    for root, dirs, files in os.walk(path):
        if not skip_hidden_dirs or \
                not (bool(os.stat(root).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
                     or os.path.split(root)[-1].startswith(".")):
            for file in files:
                file_path = os.path.join(root, file)
                if not skip_hidden_dirs \
                        or not (bool(os.stat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
                                or file.startswith(".")):
                    if suffix_list is not None:
                        for suffix in suffix_list:
                            if file.endswith(suffix):
                                yield file_path
                                break
                    else:
                        yield file_path
