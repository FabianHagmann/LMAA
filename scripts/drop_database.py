import logging
import sqlite3
import config
import yaml

config.load_logging_config()

# open database connection
logging.debug('loading system configuration for database connection')
config_stream = open('../config/system_config.yaml', 'r')
config_map = yaml.safe_load(config_stream)

logging.debug('connecting to database')
connection = sqlite3.connect('../data/' + config_map['management']['database']['name'] + '.db')
cursor = connection.cursor()
logging.info('database connection established')

# drop database
logging.debug('dropping tables')

cursor.execute("DROP TABLE IF EXISTS TESTRESULT")
cursor.execute("DROP TABLE IF EXISTS SOLUTION")
cursor.execute("DROP TABLE IF EXISTS COMPILE_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS CONTAINS_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS UNIT_TESTCASE")
cursor.execute("DROP TABLE IF EXISTS TESTCASE")
cursor.execute("DROP TABLE IF EXISTS CLASSIFICATION_TAG")
cursor.execute("DROP TABLE IF EXISTS TAG")
cursor.execute("DROP TABLE IF EXISTS CLASSIFICATION")
cursor.execute("DROP TABLE IF EXISTS TASK")

connection.commit()
logging.info('database successfully dropped')
