import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()

c = Client()
c.force_login(user)
resp = c.get('/dashboard/')
text = resp.content.decode(errors='replace')
lines = text.split('\n')
for i in range(700, 730):
    print(f"{i+1:4}: {lines[i]}")
