import logging
import os.path

import yaml

from utils import project_utils

"""
Logging configuration

Can be used by every component for configuring logging rules and output.
"""


def load_min_logging_level(level):
    """
    Converts the minimum logging level configured in 'system_config.yaml' into a logging-level conformable to the
    specification found in the python package 'logging'

    :param level: minimum logging level from 'system_comig.yaml'
    :return: converted logging level for python package 'logging'
    """
    match level:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARNING":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case _:
            return logging.INFO


def load_logging_config():
    """
    Loads the universal logging configuration for the calling component.
    Configuration:

    - minimum logging level:        defined in 'system_config.yaml'
    - logging location:             file, defined in 'system_config.yaml'
    - logging format:               '%(asctime)s | %(module)s | %(levelname)s | %(message)s'
    """

    # load configuration
    config_stream = open(os.path.join(project_utils.find_root_path(__file__), 'config', 'system_config.yaml'), 'r')
    config_map = yaml.safe_load(config_stream)

    # define logging level and file
    logging_level = load_min_logging_level(config_map['logging']['level'])
    logging_file = project_utils.find_root_path(__file__) + '/logs/' + config_map['logging']['filename']

    # set logging configuration
    logging.basicConfig(filename=logging_file, level=logging_level,
                        format='%(asctime)s | %(module)s | %(levelname)s | %('
                               'message)s')
