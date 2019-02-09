# coding=utf-8
import os
from pathlib import Path

BASE_K_FACTOR = 40
CHANNEL = os.environ.get("SLACK_CHANNEL")
SLACK_USER = os.environ.get("SLACK_USER")
DATA_FOLDER = Path(__file__).absolute().parent.joinpath('data')
SLACK_API_KEY = os.environ.get("SLACK_API_KEY")
PATHS = {"test": DATA_FOLDER / 'test_melo.csv',
         "real": DATA_FOLDER / 'melo.csv'}
