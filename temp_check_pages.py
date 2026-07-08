import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineCodingAssessment.settings')
import django
django.setup()
from django.test import Client

c = Client()
for path in ['/study-plan/', '/recruiter/candidates/', '/recruiter/reports/', '/recruiter/contest/']:
    resp = c.get(path)
    print(path, resp.status_code)
    if resp.status_code >= 400:
        print(resp.content.decode('utf-8', 'ignore')[:1200])
        print('---')
