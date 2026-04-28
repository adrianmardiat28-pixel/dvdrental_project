import os
from django.core.wsgi import get_wsgi_application

# Ini ngasih tahu Django di mana letak settings-mu yang di dalam folder double itu
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dvdrental_project.dvdrental_project.settings')

application = get_wsgi_application()
app = application