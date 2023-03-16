import logging
import os
import sqlite3

import yaml

import config
from utils import project_utils

# configure logging
config.load_logging_config()

# open database connection
logging.debug('loading system configuration for database connection')
config_stream = open(os.path.join(project_utils.find_root_path(__file__), 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)

logging.debug('connecting to database')
connection = sqlite3.connect(
    os.path.join(project_utils.find_root_path(__file__), 'data', config_map['management']['database']['name'] + '.db'))
cursor = connection.cursor()
logging.info('database connection established')

# drop database
logging.debug('dropping tables')

cursor.execute("DROP TABLE IF EXISTS TESTRESULT")
cursor.execute("DROP TABLE IF EXISTS SOLUTION")
cursor.execute("DROP TABLE IF EXISTS COMPILES_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS CONTAINS_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS UNIT_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS TESTCASE")
cursor.execute("DROP TABLE IF EXISTS TASK")
cursor.execute("DROP TABLE IF EXISTS CLASSIFICATION_TAG")
cursor.execute("DROP TABLE IF EXISTS CLASSIFICATION")
cursor.execute("DROP TABLE IF EXISTS TAG")

connection.commit()
logging.info('database successfully dropped')
