"""
WSGI config for cloud_emulator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "griptape.cli.cloud_emulator.cloud_emulator.settings"
)

application = get_wsgi_application()
