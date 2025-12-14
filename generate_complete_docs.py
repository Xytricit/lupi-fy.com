#!/usr/bin/env python3
"""Generate complete project documentation with all files."""

import os
import pathlib
from datetime import datetime

def get_all_source_files(root_path):
    """Get all source code files, excluding binaries and cache."""
    source_extensions = {
        '.py', '.js', '.html', '.css', '.md', '.txt', 
        '.json', '.yaml', '.yml', '.bat', '.ps1', '.sql'
    }
    
    exclude_patterns = {
        '.venv', '__pycache__', '.git', 'node_modules',
        '.pyc', '.env', '.pytest_cache', 'media', 'data'
    }
    
    files = []
    root = pathlib.Path(root_path)
    
    for file_path in root.rglob('*'):
        if not file_path.is_file():
            continue
            
        # Check if should exclude
        if any(exclude in str(file_path) for exclude in exclude_patterns):
            continue
            
        if file_path.suffix in source_extensions:
            files.append(file_path)
    
    return sorted(files)

def read_file_safe(file_path, max_size=100000):
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

def generate_documentation(root_path, output_file):
    """Generate complete documentation."""
    files = get_all_source_files(root_path)
    
    # Group files by type
    file_groups = {}
    for f in files:
        ext = f.suffix
        if ext not in file_groups:
            file_groups[ext] = []
        file_groups[ext].append(f)
    
    # Start building content
    content = []
    content.append("# COMPLETE PROJECT DOCUMENTATION - ALL FILES\n")
    content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"Project Root: {root_path}\n")
    content.append(f"Total Files Included: {len(files)}\n")
    content.append("---\n\n")
    
    # Summary table
    content.append("## FILE SUMMARY BY TYPE\n\n")
    for ext in sorted(file_groups.keys()):
        content.append(f"- {ext}: {len(file_groups[ext])} files\n")
    content.append("\n---\n\n")
    
    # Process each file type
    root_abs = pathlib.Path(root_path)
    
    for ext in sorted(file_groups.keys()):
        files_of_type = file_groups[ext]
        lang_hint = get_language_hint(ext)
        
        content.append(f"## {ext.upper()} FILES ({len(files_of_type)} files)\n\n")
        
        for file_path in sorted(files_of_type):
            rel_path = file_path.relative_to(root_abs)
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
    output = os.path.join(root, 'COMPLETE_PROJECT_ALL_FILES.md')
    
    print(f"Generating documentation...")
    size, count = generate_documentation(root, output)
    
    print(f"✓ Documentation created: {output}")
    print(f"✓ Total files included: {count}")
    print(f"✓ File size: {size / (1024*1024):.2f} MB")
