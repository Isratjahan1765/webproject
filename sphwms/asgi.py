"""
ASGI config for SPHWMS project.
Supports both HTTP and WebSocket protocols.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sphwms.settings')
application = get_asgi_application()
