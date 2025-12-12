import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()
print(f"Total users: {users.count()}")

if users.exists():
    user = users.first()
    print(f"User: {user.username}")
    
    # Force login
    c = Client()
    c.force_login(user)
    resp = c.get('/dashboard/')
    
    print(f"Status: {resp.status_code}")
    content = resp.content.decode()
    print(f"Has create-btn: {'create-btn' in content}")
    print(f"Has createModal: {'createModal' in content}")
    print(f"Has Lupify: {'Lupify' in content}")
    print(f"Has initCreateModal: {'initCreateModal' in content}")
    
    if 'create-btn' not in content:
        print("\nDashboard HTML preview (first 2000 chars):")
        print(content[:2000])
    else:
        print("\n[SUCCESS] Create button IS in the response!")
        # Find it
        idx = content.find('create-btn')
        print(f"\nContext around create-btn (chars {idx-100} to {idx+200}):")
        print(content[max(0, idx-100):idx+200])
