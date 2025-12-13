#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client

client = Client()
response = client.get('/')
content = response.content.decode()

# Check for sort variable
print("Checking for sort variable initialization...")
if 'let sort = ' in content:
    print("✅ Found: let sort = ")
elif 'var sort = ' in content:
    print("✅ Found: var sort = ")
elif 'sort = ' in content:
    # Find all occurrences
    lines = content.split('\n')
    found = False
    for i, line in enumerate(lines):
        if 'sort' in line and '=' in line and 'sort:' not in line:
            if not found:
                print(f"Found sort assignment: {line.strip()[:80]}")
                found = True

if not 'sort' in content:
    print("❌ No sort variable found")
    
# Check for sortChange event
if 'sortChange' in content:
    print("✅ Found: sortChange event listener")
else:
    print("❌ sortChange event not found")

# Check for DOMContentLoaded
if 'DOMContentLoaded' in content:
    print("✅ Found: DOMContentLoaded event listener")

# Check filter-bubble
if 'filter-bubble' in content:
    print("✅ Found: filter-bubble class references")
    
# Check the community feed element
if 'community-feed' in content:
    print("✅ Found: community-feed element")
