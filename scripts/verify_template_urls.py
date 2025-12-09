import os
import sys
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from django.urls import reverse, NoReverseMatch

# Search all templates for {% url 'name' %}
import glob
names = set()
for fn in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    with open(fn, 'r', encoding='utf-8') as f:
        txt = f.read()
    for m in re.finditer(r"{%\s*url\s+'([a-zA-Z0-9_:/-]+)'(?:[^%}]*)%}", txt):
        names.add(m.group(1))

print('Found url names in templates:', names)

problems = []
for name in sorted(names):
    try:
        # Try reverse with no args first
        url = reverse(name)
        print(f"OK: {name} -> {url}")
    except NoReverseMatch as e:
        # Try with a sample int arg
        try:
            url = reverse(name, args=[1])
            print(f"OK with int arg: {name} -> {url}")
        except Exception as e2:
            problems.append((name, str(e)))
            print(f"BROKEN: {name} -> {e}")

if problems:
    print('\nProblems found:')
    for p in problems:
        print(p)
else:
    print('\nAll template url names reverse (with optional int arg) OK')
