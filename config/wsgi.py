"""
WSGI config for the Safe Odds project.

Quick explanation for learning Django:
- WSGI (Web Server Gateway Interface) is the standard way Python web apps
  talk to web servers like Gunicorn.
- In production, Gunicorn uses this file to serve your Django app.
- You almost never need to edit this file.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
