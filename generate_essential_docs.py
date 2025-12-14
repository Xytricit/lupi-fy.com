#!/usr/bin/env python3
"""Generate essential project documentation - only files needed to recreate the project."""

import os
import pathlib
from datetime import datetime

def is_essential_file(file_path):
    """Determine if a file is essential for project recreation."""
    path_str = str(file_path).lower()
    name = file_path.name.lower()
    
    # Exclude patterns
    exclude = {
        '__pycache__', '.git', '.venv', 'node_modules', '.env',
        '.pyc', '.pytest_cache', 'media/', 'avatars/', 'posts/',
        'game_thumbnails', 'marketplace/thumbnails', 'community_',
        '.log', 'server.log', 'daphne.log',
        '_old.', '_backup', '_test.', 'test_results.txt',
        'db.sqlite3',  # Database file
        'generate_complete_docs.py',
        'debug_', 'check_', 'quick_test',
    }
    
    # Check exclusions
    for pattern in exclude:
        if pattern in path_str:
            return False
    
    # Exclude temp/old HTML
    if name in {'blog_old.html', 'subscriptions_old.html', 'dashboard.html', 'dash_live.html'}:
        return False
    
    # Exclude unnecessary docs
    if name.endswith('.md'):
        # Keep essential docs only
        keep_docs = {
            'readme.md', 'requirements.txt', 'render.yaml',
            'architecture.md', 'setup_checklist.md'
        }
        if name not in keep_docs:
            return False
    
    return True

def get_essential_files(root_path):
    """Get only essential files for project recreation."""
    source_extensions = {
        '.py', '.js', '.html', '.css', '.md', '.txt', 
        '.json', '.yaml', '.yml', '.bat', '.ps1'
    }
    
    files = []
    root = pathlib.Path(root_path)
    
    for file_path in root.rglob('*'):
        if not file_path.is_file():
            continue
        
        if file_path.suffix not in source_extensions:
            continue
        
        if is_essential_file(file_path):
            files.append(file_path)
    
    return sorted(files)

def read_file_safe(file_path, max_size=50000):
    """Safely read file content."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if len(content) > max_size:
                return content[:max_size] + f"\n\n[... File truncated. Total length: {len(content)} chars ...]"
            return content
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

def get_language_hint(extension):
    """Get language hint for code block."""
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sql': 'sql',
        '.bat': 'batch',
        '.ps1': 'powershell',
        '.txt': 'text',
        '.md': 'markdown'
    }
    return mapping.get(extension, 'text')

def group_files_by_category(files, root_abs):
    """Organize files into logical categories."""
    categories = {
        'Core Configuration': [],
        'Main Project Settings': [],
        'Django Apps - Core': [],
        'Django Apps - Blog': [],
        'Django Apps - Accounts': [],
        'Django Apps - Games': [],
        'Django Apps - Communities': [],
        'Django Apps - Recommendations': [],
        'Django Apps - Marketplace': [],
        'Django Apps - Chatbot': [],
        'Templates': [],
        'Static Files': [],
        'Scripts & Utilities': [],
        'Documentation': []
    }
    
    for f in files:
        rel_path = str(f.relative_to(root_abs)).lower()
        
        if 'requirements.txt' in rel_path or 'render.yaml' in rel_path or 'manage.py' in rel_path:
            categories['Core Configuration'].append(f)
        elif rel_path.startswith('mysite/'):
            categories['Main Project Settings'].append(f)
        elif rel_path.startswith('core/') and '__pycache__' not in rel_path:
            categories['Django Apps - Core'].append(f)
        elif rel_path.startswith('blog/') and '__pycache__' not in rel_path:
            categories['Django Apps - Blog'].append(f)
        elif rel_path.startswith('accounts/') and '__pycache__' not in rel_path:
            categories['Django Apps - Accounts'].append(f)
        elif rel_path.startswith('games/') and '__pycache__' not in rel_path:
            categories['Django Apps - Games'].append(f)
        elif rel_path.startswith('communities/') and '__pycache__' not in rel_path:
            categories['Django Apps - Communities'].append(f)
        elif rel_path.startswith('recommend/') and '__pycache__' not in rel_path:
            categories['Django Apps - Recommendations'].append(f)
        elif rel_path.startswith('marketplace/') and '__pycache__' not in rel_path:
            categories['Django Apps - Marketplace'].append(f)
        elif rel_path.startswith('chatbot/'):
            categories['Django Apps - Chatbot'].append(f)
        elif rel_path.startswith('templates/'):
            categories['Templates'].append(f)
        elif rel_path.startswith('static/'):
            categories['Static Files'].append(f)
        elif rel_path.startswith('scripts/'):
            categories['Scripts & Utilities'].append(f)
        elif rel_path.endswith('.md'):
            categories['Documentation'].append(f)
        else:
            categories['Scripts & Utilities'].append(f)
    
    return {k: v for k, v in categories.items() if v}

def generate_documentation(root_path, output_file):
    """Generate essential documentation."""
    files = get_essential_files(root_path)
    
    if not files:
        print("No essential files found!")
        return 0, 0
    
    root_abs = pathlib.Path(root_path)
    categories = group_files_by_category(files, root_abs)
    
    # Start building content
    content = []
    content.append("# ESSENTIAL PROJECT DOCUMENTATION\n\n")
    content.append("**For Project Recreation**\n\n")
    content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"Total Files: {len(files)}\n\n")
    
    content.append("## SETUP INSTRUCTIONS\n\n")
    content.append("1. Create a virtual environment: `python -m venv .venv`\n")
    content.append("2. Activate it: `.venv\\Scripts\\activate`\n")
    content.append("3. Install dependencies: `pip install -r requirements.txt`\n")
    content.append("4. Run migrations: `python manage.py migrate`\n")
    content.append("5. Create superuser: `python manage.py createsuperuser`\n")
    content.append("6. Run server: `python manage.py runserver`\n\n")
    
    content.append("---\n\n")
    
    # Table of contents
    content.append("## TABLE OF CONTENTS\n\n")
    for category in categories.keys():
        content.append(f"- {category} ({len(categories[category])} files)\n")
    content.append("\n---\n\n")
    
    # Process each category
    for category, files_in_category in categories.items():
        content.append(f"## {category.upper()} ({len(files_in_category)} files)\n\n")
        
        for file_path in sorted(files_in_category):
            rel_path = file_path.relative_to(root_abs)
            lang_hint = get_language_hint(file_path.suffix)
            
            content.append(f"### {rel_path}\n\n")
            content.append(f"```{lang_hint}\n")
            
            file_content = read_file_safe(file_path)
            content.append(file_content)
            
            content.append("\n```\n\n")
        
        content.append("---\n\n")
    
    # Write output
    output_path = pathlib.Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    return output_path.stat().st_size, len(files)

if __name__ == '__main__':
    root = r'C:\Users\turbo\OneDrive\Documents\GitHub\lupi-fy.com'
    output = os.path.join(root, 'PROJECT_ESSENTIAL_FILES.md')
    
    print(f"Generating essential documentation...")
    size, count = generate_documentation(root, output)
    
    if count > 0:
        print(f"✓ Documentation created: {output}")
        print(f"✓ Total essential files: {count}")
        print(f"✓ File size: {size / (1024*1024):.2f} MB")
    else:
        print("No files processed!")
