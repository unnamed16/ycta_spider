__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2020/05/19'

import os
import json
from pathlib import Path
from typing import Any, AnyStr, Union, Iterable

import pandas as pd
import fasteners

from ycta_spider.file_manager.reader import ROOT_FOLDER, CONFIG_PATH

__CONFIG_LOCK = fasteners.InterProcessReaderWriterLock(os.path.join(ROOT_FOLDER, 'config.lock'))

def save_config(config: dict):
    """if you've made any changes to the config, save using this fcn to avoid race conditions"""
    with __CONFIG_LOCK.write_lock():
        save_json(config, CONFIG_PATH)

def save_file(data: AnyStr, path: Union[str, Path]) -> None:
    """
    Save data to a file\n
    :param data: data to save
    :param path: string with the path to an output file
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding="utf8") as f:
        f.write(data)


def save_json(data: Any, path: Union[str, Path]) -> None:
    """
    Save data to a JSON file\n
    :param data: data to save
    :param path: string with the path to an output file
    """
    save_file(json.dumps(data, indent=2), path)


def save_csv(data: Iterable[Iterable[Any]], path: Union[str, Path], headers: Iterable[str] = None) -> None:
    """
    Save data to a CSV file\n
    :param data: data to save
    :param path: string with the path to an output file
    :param headers: first line of the csv (expected names of columns)
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    pd.DataFrame(data=data, columns=headers).to_csv(path, sep=u'\001', index=False, line_terminator='\n')

