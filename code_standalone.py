# In your standalone_script.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from your_app_name.models import MyModel

# Now you can use MyModel
instance = MyModel.objects.create(name="Example")