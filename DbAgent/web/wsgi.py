"""
WSGI config for the DbAgent web interface.

Exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import sys

# Ensure src/ is on the path so Django can import agent modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

application = get_wsgi_application()