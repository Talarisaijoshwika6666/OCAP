import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineCodingAssessment.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
user, created = User.objects.get_or_create(username='candidate1', defaults={'email': 'candidate1@example.com'})
user.set_password('pass12345')
user.save()

c = Client()
c.force_login(user)
for path in ['/study-plan/', '/study-plan/data-structures/', '/quest/']:
    resp = c.get(path)
    print(path, resp.status_code)
