#!/usr/bin/env python3
"""Try to parse and find syntax error"""
import ast
import sys

try:
    with open('ciaf/industries/biotechnology.py', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print("File parses successfully!")
except SyntaxError as e:
    print(f"Syntax Error at line {e.lineno}: {e.msg}")
    print(f"Text: {e.text}")
    
    # Try to find unclosed strings by examining the file
    lines = content.split('\n')
    in_docstring = False
    docstring_start = None
    for i, line in enumerate(lines, 1):
        triple_count = line.count('"""')
        if triple_count % 2 == 1:  # Odd number means we're toggling
            if not in_docstring:
                in_docstring = True
                docstring_start = i
                print(f"  Docstring opened at line {i}: {line[:60]}")
            else:
                in_docstring = False
                print(f"  Docstring closed at line {i} (opened at {docstring_start})")
                docstring_start = None
    
    if in_docstring:
        print(f"\nUNCLOSED DOCSTRING starting at line {docstring_start}!")
