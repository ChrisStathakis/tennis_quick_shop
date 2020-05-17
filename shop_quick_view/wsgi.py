import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_quick_view.settings')

application = get_wsgi_application()
application = WhiteNoise(application)
# application.add_files('/path/to/more/static/files', prefix='more-files/')