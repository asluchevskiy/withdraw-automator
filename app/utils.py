# -*- coding: utf-8 -*-
import csv
import logging
import random
import colorlog


def load_lines(filename):
    with open(filename) as f:
        return [row.strip() for row in f if row and not row.startswith('#')]


def load_csv(filename):
    with open(filename) as f:
        return [row for row in csv.reader(f)]


log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  # log message formatting

color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white,bold',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    reset=True,
    style='%'
)


def random_float(a, b, diff=1):
    random_number = random.uniform(a, b)
    try:
        precision_a = len(str(a).split('.')[1])
    except IndexError:
        precision_a = 0
    try:
        precision_b = len(str(b).split('.')[1])
    except IndexError:
        precision_b = 0
    precision = max(precision_a, precision_b)
    return round(random_number, precision + diff)


def setup_file_logging(logger, log_file):
    # logging file handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)


def setup_color_logging(logger):
    handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    handler.setFormatter(color_formatter)
    # handler.setFormatter(log_formatter)
    logger.addHandler(handler)
