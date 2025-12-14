#!/usr/bin/env python3
"""
Project Splitter for Claude AI
Splits a project into manageable chunks for Claude AI consumption.
"""

import os
import pathlib
from pathlib import Path
from collections import defaultdict
import mimetypes

# Configuration
CHUNK_MAX_LINES = 4500
BINARY_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.o', '.a', '.out',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp',
    '.mp3', '.mp4', '.wav', '.flv', '.mov', '.avi',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.dll',
    '.pdf', '.xlsx', '.docx', '.pptx',
    '.db', '.sqlite', '.sqlite3',
    '.class', '.jar'
}

SKIP_PATTERNS = {
    '__pycache__', '.git', '.gitignore', '.env', '.venv', 'venv',
    'node_modules', '.pytest_cache', '.coverage', 'dist', 'build',
    '.egg-info', '.DS_Store', '.idea', '.vscode', '.mypy_cache',
    'htmlcov', '.tox', '.nox', 'site-packages', '*.lock'
}

ENTRY_POINT_FILES = {
    'main.py', 'app.py', 'manage.py', 'run.py', 'server.py',
    'wsgi.py', 'asgi.py', 'cli.py', '__main__.py', 'index.py'
}

SOURCE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c',
    '.h', '.hpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift',
    '.kt', '.scala', '.groovy', '.sql', '.sh', '.bash', '.ps1',
    '.yaml', '.yml', '.json', '.xml', '.html', '.css', '.scss',
    '.sass', '.less', '.md', '.markdown', '.txt', '.toml', '.ini',
    '.cfg', '.conf', '.gradle', '.maven', '.cargo', '.lock'
}


def should_skip_path(path_obj, relative_path):
    """Check if path should be skipped."""
    if path_obj.is_dir():
        return any(pattern in relative_path.parts for pattern in SKIP_PATTERNS)
    return False


def is_source_file(file_path):
    """Check if file is a source code file."""
    suffix = Path(file_path).suffix.lower()
    
    if suffix in BINARY_EXTENSIONS:
        return False
    
    if suffix in SOURCE_EXTENSIONS:
        return True
    
    if suffix == '':
        name = Path(file_path).name
        if name in {'Dockerfile', 'Makefile', 'Rakefile', 'Gemfile', 'Procfile'}:
            return True
        if name.startswith('.') and name not in {'.env', '.gitignore'}:
            return False
    
    return False


def read_file_safe(file_path):
    """Safely read file content, handling encoding issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return None
    except Exception:
        return None


def get_folder_structure(root_path, max_depth=3):
    """Generate folder structure representation."""
    def build_tree(path, prefix="", current_depth=0):
        if current_depth >= max_depth:
            return ""
        
        try:
            items = sorted(path.iterdir())
        except PermissionError:
            return ""
        
        tree = ""
        dirs = [item for item in items if item.is_dir() and not should_skip_path(item, item.relative_to(root_path))]
        files = [item for item in items if item.is_file()]
        
        for i, item in enumerate(dirs + files[:10]):
            is_last = i == len(dirs + files[:10]) - 1
            current_prefix = "└── " if is_last else "├── "
            tree += f"{prefix}{current_prefix}{item.name}\n"
            
            if item.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree += build_tree(item, next_prefix, current_depth + 1)
        
        if len(files) > 10:
            tree += f"{prefix}    ... and {len(files) - 10} more files\n"
        
        return tree
    
    return build_tree(root_path)


def find_entry_points(root_path):
    """Find potential entry point files."""
    entry_points = []
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and file_path.name in ENTRY_POINT_FILES:
            try:
                rel_path = file_path.relative_to(root_path)
                entry_points.append(str(rel_path).replace('\\', '/'))
            except ValueError:
                pass
    
    return sorted(entry_points)


def collect_source_files(root_path):
    """Collect all source files recursively."""
    source_files = []
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file():
            try:
                rel_path = file_path.relative_to(root_path)
                
                if should_skip_path(file_path, rel_path):
                    continue
                
                if is_source_file(file_path):
                    source_files.append(file_path)
            except ValueError:
                pass
    
    return sorted(source_files)


def get_module_path(file_path, root_path):
    """Get module path for file (e.g., 'src.core.auth')."""
    try:
        rel_path = file_path.relative_to(root_path)
        parts = rel_path.parts[:-1]
        return '.'.join(parts) if parts else 'root'
    except ValueError:
        return 'root'


def create_chunks(source_files, root_path, output_dir):
    """Create chunks from source files."""
    module_files = defaultdict(list)
    
    for file_path in source_files:
        module = get_module_path(file_path, root_path)
        module_files[module].append(file_path)
    
    chunk_files = []
    manifest = []
    
    for module_idx, (module, files) in enumerate(sorted(module_files.items())):
        chunk_num = 1
        current_lines = 0
        current_content = ""
        current_files = []
        
        for file_path in sorted(files):
            content = read_file_safe(file_path)
            
            if content is None:
                continue
            
            try:
                rel_path = file_path.relative_to(root_path)
            except ValueError:
                rel_path = file_path
            
            file_lines = len(content.split('\n'))
            
            if current_lines + file_lines > CHUNK_MAX_LINES and current_content:
                chunk_filename = create_chunk_file(
                    output_dir, module, chunk_num, current_content, current_files
                )
                chunk_files.append(chunk_filename)
                manifest.append({
                    'file': chunk_filename,
                    'module': module,
                    'chunk': chunk_num,
                    'lines': current_lines,
                    'file_count': len(current_files)
                })
                
                chunk_num += 1
                current_lines = 0
                current_content = ""
                current_files = []
            
            file_header = f"\n\n{'='*80}\nFILE: {rel_path}\n{'='*80}\n\n"
            current_content += file_header + content
            current_lines += file_lines
            current_files.append(str(rel_path).replace('\\', '/'))
        
        if current_content:
            chunk_filename = create_chunk_file(
                output_dir, module, chunk_num, current_content, current_files
            )
            chunk_files.append(chunk_filename)
            manifest.append({
                'file': chunk_filename,
                'module': module,
                'chunk': chunk_num,
                'lines': current_lines,
                'file_count': len(current_files)
            })
    
    return chunk_files, manifest


def create_chunk_file(output_dir, module, chunk_num, content, files):
    """Create a single chunk file."""
    safe_module = module.replace('.', '_')
    chunk_name = f"{safe_module}_chunk{chunk_num}.txt"
    chunk_path = output_dir / chunk_name
    
    header = f"""FILE GROUP: {module}
CHUNK: {chunk_num}
FILES INCLUDED:
"""
    for file in files:
        header += f"  - {file}\n"
    
    header += f"\nTOTAL LINES: {len(content.split(chr(10)))}\n"
    header += "=" * 80 + "\n\n"
    
    with open(chunk_path, 'w', encoding='utf-8') as f:
        f.write(header + content)
    
    return chunk_name


def create_project_overview(root_path, entry_points, source_files_count):
    """Create PROJECT_OVERVIEW.md."""
    folder_structure = get_folder_structure(root_path)
    
    content = f"""# Project Overview

## Project Description
[Edit this section with your project description]

This is a Python/Django project that contains multiple modules for handling various functionalities.

## Project Statistics

- **Total Source Files**: {source_files_count}
- **Entry Points**: {len(entry_points)}

## Folder Structure

\`\`\`
{folder_structure}\`\`\`

## Entry Points

Entry points detected:

"""
    for entry in entry_points:
        content += f"- `{entry}`\n"
    
    content += """
## Coding Rules & Guidelines

[Edit this section with your coding standards]

### Python Standards
- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Maximum line length: 88 characters (Black formatter)

### Testing
- All new features must include tests
- Maintain test coverage above 80%
- Use pytest for testing

### Version Control
- Commit messages should be descriptive
- Use feature branches
- Keep commits atomic and logical

## How to Use with Claude AI

1. Start with this overview file
2. Upload chunks incrementally to Claude
3. Reference specific file groups and modules
4. Use the claude_chunks/MANIFEST.md for organization

## Next Steps

- [ ] Review and customize this overview
- [ ] Upload chunks to Claude in order
- [ ] Reference specific files when discussing features
- [ ] Update with project-specific information
"""
    
    overview_path = root_path / "PROJECT_OVERVIEW.md"
    with open(overview_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return overview_path


def create_chunk_readme(output_dir, chunk_files, manifest):
    """Create README.md for claude_chunks directory."""
    content = """# Claude AI Chunks

This directory contains your project split into manageable chunks for uploading to Claude AI.

## Overview

Each chunk is a text file containing source code from related modules. This splitting allows you to:
- Upload large projects incrementally
- Stay within Claude's context limits
- Organize code by module/functionality

## Manifest

See `MANIFEST.md` for a complete list of all chunks and their contents.

## How to Use

### Step 1: Start with Project Overview
First, upload `PROJECT_OVERVIEW.md` from the project root. This gives Claude context about your project structure.

### Step 2: Upload Chunks Incrementally
Upload chunks in the order specified in `MANIFEST.md`. For example:

1. Start with root-level modules
2. Progress to sub-modules
3. Ask Claude questions about specific modules

### Step 3: Reference Specific Files
When asking Claude about a specific file, mention:
- The chunk file name (e.g., `src_core_auth_chunk1.txt`)
- The specific file within that chunk (listed in the header)

## Chunk Structure

Each chunk file has:
```
FILE GROUP: [module/folder name]
CHUNK: [number]
FILES INCLUDED:
  - file1
  - file2
  ...
TOTAL LINES: [line count]
```

Followed by the actual source code from those files.

## Important Notes

- **Max lines per chunk**: ~4500 lines (to stay within context)
- **Binary files**: Already excluded (images, compiled code, etc.)
- **Folder structure**: Preserved in filenames (e.g., `src_core_auth_chunk1.txt`)

## Recommended Upload Strategy

1. **First context**: PROJECT_OVERVIEW.md + root_chunk files
2. **Second context**: Core modules (src/core or similar)
3. **Subsequent contexts**: Feature-specific chunks
4. **For changes**: Only upload relevant chunks + MANIFEST.md

## Example Conversation with Claude

> "I'm uploading my project in chunks. Here's the overview and root chunks. What's the main architecture?"

> "Now I'm adding the authentication module. Can you review it?"

> "Here's the database layer. How should I improve this?"

## File Organization

```
claude_chunks/
├── README.md (this file)
├── MANIFEST.md (complete file list)
├── root_chunk1.txt
├── src_core_auth_chunk1.txt
├── src_core_auth_chunk2.txt
├── src_models_chunk1.txt
├── ...
```

## Best Practices

- Always include MANIFEST.md when uploading a new set
- Keep chunks in the same conversation when possible
- Ask Claude to summarize what it's learned before moving to new chunks
- Use specific file names when referencing code
- Save Claude's responses for future reference

---

Generated by: split_project_for_claude.py
"""
    
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_manifest(output_dir, manifest):
    """Create MANIFEST.md listing all chunks."""
    content = """# Chunks Manifest

This is a complete manifest of all chunks created from your project.

## Summary

"""
    content += f"- **Total Chunks**: {len(manifest)}\n"
    content += f"- **Total Files**: {sum(m['file_count'] for m in manifest)}\n"
    content += f"- **Total Lines**: {sum(m['lines'] for m in manifest)}\n\n"
    
    content += "## Chunks by Module\n\n"
    
    current_module = None
    for item in manifest:
        if item['module'] != current_module:
            current_module = item['module']
            content += f"### {current_module}\n\n"
        
        content += f"**{item['file']}** (Chunk {item['chunk']})\n"
        content += f"- Lines: {item['lines']}\n"
        content += f"- Files: {item['file_count']}\n\n"
    
    content += """## Upload Order Recommendation

Upload chunks in the order listed above. If your project has dependencies:

1. Start with root-level modules
2. Then core/base modules
3. Then feature-specific modules
4. Finally, utility/helper modules

## How to Upload

### For each context with Claude:

1. Copy the chunk file content
2. Paste into Claude with context like:
   ```
   Analyzing [chunk_file_name]
   This chunk is from the [module_name] module
   ```
3. Ask your questions about that chunk
4. Move to next chunk when ready

### Full project analysis:

1. Upload PROJECT_OVERVIEW.md first
2. Upload all MANIFEST files with their chunks
3. Ask Claude to analyze the architecture
4. Ask specific questions about modules

---

Last generated: """
    
    import datetime
    content += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    manifest_path = output_dir / "MANIFEST.md"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """Main execution function."""
    root_path = Path.cwd()
    
    print(f"[*] Scanning project: {root_path}")
    
    source_files = collect_source_files(root_path)
    entry_points = find_entry_points(root_path)
    
    print(f"[*] Found {len(source_files)} source files")
    print(f"[*] Found {len(entry_points)} entry points")
    
    output_dir = root_path / "claude_chunks"
    output_dir.mkdir(exist_ok=True)
    
    print(f"[*] Creating chunks...")
    chunk_files, manifest = create_chunks(source_files, root_path, output_dir)
    
    print(f"[*] Created {len(chunk_files)} chunk files")
    
    print(f"[*] Creating PROJECT_OVERVIEW.md...")
    create_project_overview(root_path, entry_points, len(source_files))
    
    print(f"[*] Creating documentation in claude_chunks/...")
    create_chunk_readme(output_dir, chunk_files, manifest)
    create_manifest(output_dir, manifest)
    
    print(f"\n[✓] Done!")
    print(f"\nOutput:")
    print(f"  - PROJECT_OVERVIEW.md (in project root)")
    print(f"  - claude_chunks/ (directory with all chunks)")
    print(f"    - README.md")
    print(f"    - MANIFEST.md")
    print(f"    - {len(chunk_files)} chunk files")
    print(f"\nTotal lines in chunks: {sum(m['lines'] for m in manifest)}")


if __name__ == "__main__":
    main()
