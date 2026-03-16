#!/usr/bin/env python3
"""
Fix all deprecated datetime.utcnow() calls in the codebase.
Replaces with datetime.now(timezone.utc)
"""
import os
import re
from pathlib import Path

def fix_utcnow_in_file(filepath):
    """Fix utcnow() calls in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if timezone is imported
        has_timezone_import = 'from datetime import' in content and 'timezone' in content
        
        # Add timezone to datetime imports if needed
        if 'from datetime import' in content and not has_timezone_import:
            # Find the datetime import line
            import_pattern = r'from datetime import ([^\n]+)'
            match = re.search(import_pattern, content)
            if match:
                imports = match.group(1)
                if 'timezone' not in imports:
                    new_imports = imports.rstrip() + ', timezone'
                    content = content.replace(
                        f'from datetime import {imports}',
                        f'from datetime import {new_imports}'
                    )
        
        # Replace datetime.utcnow() with datetime.now(timezone.utc)
        content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
        
        # Replace standalone utcnow() with now(timezone.utc) - for cases with `from datetime import utcnow`
        content = content.replace('utcnow()', 'datetime.now(timezone.utc)')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the codebase"""
    base_dir = Path('.')
    
    # Directories to process
    dirs_to_process = [
        'tests',
        'ciaf',
        'ciaf_client',
        'agents_base.py',
        'Data/LLM',
        'model/LLM',
    ]
    
    fixed_count = 0
    
    for dir_path in dirs_to_process:
        path = base_dir / dir_path
        if not path.exists():
            continue
            
        if path.is_file():
            if fix_utcnow_in_file(path):
                print(f"Fixed: {path}")
                fixed_count += 1
        else:
            for py_file in path.rglob('*.py'):
                if fix_utcnow_in_file(py_file):
                    print(f"Fixed: {py_file}")
                    fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
