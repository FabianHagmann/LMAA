import argparse
import os
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

# parse arguments
parser = argparse.ArgumentParser(
    prog='Setup script for LMAA',
    description='Setup database and logging')
args = parser.parse_args()

# create database dir
db_dirname = "data"
db_path = os.path.join(os.getcwd(), db_dirname)

try:
    if not os.path.exists(db_path):
        os.makedirs(db_path)
except OSError:
    raise SystemExit(f'Error trying to setup the database-directory \'{db_path}\'')

# create logs dir
log_dirname = "logs"
log_path = os.path.join(os.getcwd(), log_dirname)

try:
    if not os.path.exists(log_path):
        os.makedirs(log_path)
except OSError:
    raise SystemExit(f'Error trying to setup the log-directory \'{log_path}\'')


# migrate database
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmaa.settings')
    app = get_wsgi_application()
    call_command('migrate')
except Exception as e:
    raise SystemExit(f'Error trying to migrate database\n' + str(e) + "\n" + "(Make sure all requirements are installed)")
