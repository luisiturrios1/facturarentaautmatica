"""
WSGI config for alvisarrentas project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alvisarrentas.settings")

application = get_wsgi_application()
