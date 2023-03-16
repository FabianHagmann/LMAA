import logging
import os.path
import sqlite3
import subprocess

import yaml

import config
from utils import project_utils

# configure logging
config.load_logging_config()

# drop existing database if exists
logging.info("dropping existing database")
subprocess.run(["python", "drop_database.py"])

# open database connection
logging.debug('loading system configuration for database connection')
config_stream = open(os.path.join(project_utils.find_root_path(__file__), 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)

logging.debug('connecting to database')
connection = sqlite3.connect(
    os.path.join(project_utils.find_root_path(__file__), 'data', config_map['management']['database']['name'] + '.db'))
cursor = connection.cursor()
logging.info('database connection established')

# fetch necessary configuration information
logging.debug('fetching maxlength information')
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']
solution_maxlength = config_map['management']['database']['maxlength']['solution']

# create database
logging.debug('creating tables')

cursor.execute("CREATE TABLE TAG("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT, "
               "NAME VARCHAR(64) NOT NULL"
               ")")

cursor.execute("CREATE TABLE CLASSIFICATION("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT, "
               "EFFORT INTEGER CHECK (EFFORT >= 1 AND EFFORT <= 5),"
               "SCOPE INTEGER CHECK (SCOPE >= 1 AND SCOPE <= 5)"
               ")")

cursor.execute("CREATE TABLE CLASSIFICATION_TAG("
               "CLASSIFICATION_ID INTEGER REFERENCES CLASSIFICATION(ID),"
               "TAG_ID INTEGER REFERENCES CLASSIFICATION_TYPE(ID),"
               "PRIMARY KEY (CLASSIFICATION_ID, TAG_ID)"
               ")")

cursor.execute("CREATE TABLE TASK("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
               "SEMESTER VARCHAR(5),"
               "SHEET INTEGER,"
               "TASK INTEGER,"
               "SUBTASK VARCHAR(8),"
               "ASSIGNMENT VARCHAR(" + str(assignment_maxlength) + ") NOT NULL,"
                                                                   "CLASSIFICATION_ID INTEGER REFERENCES CLASSIFICATION(ID)"
                                                                   ")")

cursor.execute("CREATE TABLE TESTCASE("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
               "TASK_ID INTEGER REFERENCES TASK(ID) NOT NULL"
               ")")

cursor.execute("CREATE TABLE COMPILES_TESTCASE("
               "TESTCASE_ID INTEGER PRIMARY KEY REFERENCES TESTCASE(ID),"
               "ACTIVE boolean NOT NULL"
               ")")

cursor.execute("CREATE TABLE CONTAINS_TESTCASE("
               "TESTCASE_ID INTEGER PRIMARY KEY REFERENCES TESTCASE(ID),"
               "PHRASE VARCHAR(64) NOT NULL,"
               "TIMES INTEGER"
               ")")

cursor.execute("CREATE TABLE UNIT_TESTCASE("
               "TESTCASE_ID INTEGER PRIMARY KEY REFERENCES TESTCASE(ID),"
               "FILE blob NOT NULL"
               ")")

cursor.execute("CREATE TABLE SOLUTION("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
               "TIMESTAMP TIMESTAMP NOT NULL,"
               "MODEL VARCHAR(32) NOT NULL,"
               "SOLUTION VARCHAR(" + str(solution_maxlength) + ") NOT NULL,"
                                                               "TASK INTEGER REFERENCES TASK(ID) NOT NULL"
                                                               ")")

cursor.execute("CREATE TABLE TESTRESULT("
               "SOLUTION_ID INTEGER REFERENCES SOLUTION(ID),"
               "TESTCASE_ID INTEGER REFERENCES TESTCASE(ID),"
               "TIMESTAMP TIMESTAMP,"
               "RESULT boolean NOT NULL,"
               "MESSAGE VARCHAR(1024),"
               "PRIMARY KEY (SOLUTION_ID, TESTCASE_ID, TIMESTAMP)"
               ")")

connection.commit()
logging.info('database successfully created')
