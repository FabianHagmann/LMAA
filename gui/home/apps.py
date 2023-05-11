import os

import markdown
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from utils import project_utils


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gui.home'

    def ready(self):
        __update_markdown_html__()


def __update_markdown_html__():
    input = os.path.join(project_utils.find_root_path(__file__), 'README.md')
    output = os.path.join(project_utils.find_root_path(__file__), 'templates', 'home', 'readme.html')
    with open(input, 'r') as _in, open(output, 'w') as _out:
        text = _in.read()
        html = markdown.markdown(text)
        _out.write(html)
