import os

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bday_tgbot.settings')


if settings.DEBUG:
    application = get_wsgi_application()
else:
    application = StaticFilesHandler(get_wsgi_application())
