#!/usr/bin/env python3
"""Find unclosed docstrings in climate_esg.py"""
import sys

with open('ciaf/industries/climate_esg.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Finding all lines with \"\"\":")
triple_quote_lines = []
for i, line in enumerate(lines, 1):
    if '"""' in line:
        count = line.count('"""')
        triple_quote_lines.append((i, count, line.strip()[:70]))

print(f"Total \"\"\" occurrences: {sum(count for _, count, _ in triple_quote_lines)}")

if sum(count for _, count, _ in triple_quote_lines) % 2 == 1:
    print("\nUNCLOSED DOCSTRING - Analyzing...")
    in_string = False
    open_line = None
    for line_num, count, text in triple_quote_lines:
        for _ in range(count):
            if not in_string:
                in_string = True
                open_line = line_num
                print(f"  Opened at line {line_num}")
            else:
                in_string = False
                print(f"  Closed at line {line_num} (opened at {open_line})")
                open_line = None
    
    if in_string:
        print(f"\n❌ UNCLOSED: Docstring opened at line {open_line} is never closed!")
else:
    print("✅ All docstrings properly paired")
