import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup

User = get_user_model()
user = User.objects.first()

c = Client()
c.force_login(user)
resp = c.get('/dashboard/')
content = resp.content.decode()

# Extract the JavaScript code
import re

# Find the initCreateModal function
pattern = r'function initCreateModal\(\) \{.*?\}\)\(\);'
match = re.search(pattern, content, re.DOTALL)

if match:
    js_code = match.group(0)
    print("Found initCreateModal function")
    print("JavaScript code:")
    print(js_code)
    print("\n" + "="*50)
    
    # Check if the selectors match actual HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    create_btn = soup.find(class_='create-btn')
    create_modal = soup.find(id='createModal')
    blog_post_btn = soup.find(id='blog-post')
    community_post_btn = soup.find(id='community-post')
    
    print(f"\nHTML Elements found:")
    print(f"  .create-btn: {create_btn is not None}")
    print(f"  #createModal: {create_modal is not None}")
    print(f"  #blog-post: {blog_post_btn is not None}")
    print(f"  #community-post: {community_post_btn is not None}")
else:
    print("ERROR: Could not find initCreateModal function in page")
