import logging
import yaml
import os

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def load_min_logging_level(level):
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
    config_stream = open(CONFIG_DIR + '\system_config.yaml', 'r')
    config_map = yaml.safe_load(config_stream)

    logging_level = load_min_logging_level(config_map['logging']['level'])
    logging_file = '../logs/' + config_map['logging']['filename']

    logging.basicConfig(filename=logging_file, level=logging_level, format='%(asctime)s | %(name)s | %(levelname)s | %('
                                                                           'message)s')
