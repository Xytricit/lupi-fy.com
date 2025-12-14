#!/usr/bin/env python3
"""Build a zip package of essential project files for reconstruction by an AI.

Rules:
- Include: .py, .html, .css, .js, .md, .json, .yaml, .yml, .txt, .bat, .ps1
- Exclude: .venv, node_modules, .git, __pycache__, media, data, avatars, db.sqlite3, *.pyc, *.log
"""
import os
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Users\turbo\OneDrive\Documents\GitHub\lupi-fy.com")
OUT = ROOT / 'lupi-fy_essential_package.zip'

INCLUDE_EXT = {'.py', '.html', '.css', '.js', '.md', '.json', '.yaml', '.yml', '.txt', '.bat', '.ps1'}
EXCLUDE_PATTERNS = ['.venv', 'node_modules', '.git', '__pycache__', 'media', 'data', 'avatars', 'db.sqlite3']
EXCLUDE_SUFFIXES = {'.pyc', '.log', '.sqlite3', '.zip'}

files_added = 0

with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        s = str(rel).lower().replace('\\', '/')
        # Exclude patterns
        if any(p in s for p in EXCLUDE_PATTERNS):
            continue
        if any(s.endswith(suf) for suf in EXCLUDE_SUFFIXES):
            continue
        if path.suffix.lower() not in INCLUDE_EXT:
            continue
        # Add file
        zf.write(path, arcname=str(rel))
        files_added += 1

size = OUT.stat().st_size if OUT.exists() else 0
print(f"Created: {OUT}")
print(f"Files added: {files_added}")
print(f"Package size: {size/(1024*1024):.2f} MB")
