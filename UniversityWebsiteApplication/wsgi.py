"""
WSGI config for UniversityWebsiteApplication project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
import UniversityWebsiteApplication.settings as wa

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniversityWebsiteApplication.settings')
project_folder = os.path.expanduser(wa.BASE_DIR)  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '/UniversityWebsiteApplication/.env'))

application = get_wsgi_application()
