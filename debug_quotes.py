#!/usr/bin/env python3
"""Debug triple-quote matching"""
import sys

with open('ciaf/industries/biotechnology.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Finding all lines with \"\"\":")
triple_quote_lines = []
for i, line in enumerate(lines, 1):
    if '"""' in line:
        count = line.count('"""')
        triple_quote_lines.append((i, count, line.strip()[:70]))
        print(f"Line {i}: {'"""'} appears {count} time(s) - {line.strip()[:70]}")

print(f"\nTotal lines with \"\"\": {len(triple_quote_lines)}")
total_quotes = sum(count for _, count, _ in triple_quote_lines)
print(f"Total \"\"\" occurrences: {total_quotes}")

if total_quotes % 2 == 1:
    print("\n⚠️  ODD NUMBER - There's an unclosed triple-quoted string!")
    print("\nAnalyzing pairing...")
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
    print("\n✅ Even number - all docstrings should be properly paired")
