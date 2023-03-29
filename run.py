import argparse
import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

# parse arguments
parser = argparse.ArgumentParser(
    prog='Start LMAA Application',
    description='Start application')
args = parser.parse_args()

# get application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lmaa.settings')
app = get_wsgi_application()
call_command('runserver', '127.0.0.1:8000')