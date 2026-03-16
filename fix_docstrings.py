#!/usr/bin/env python3
"""Fix malformed docstrings in test_multi_framework_integration.py"""

with open('tests/test_multi_framework_integration.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove escaped quotes patterns
content = content.replace(r'\"\"\"', '"""')
content = content.replace(r'\"\"\/', '"""')
content = content.replace(r'\"\"\\', '""')

# Remove duplicate consecutive docstrings
import re
content = re.sub(r'"""([^"]+)"""\s*"""[^"]+"""', r'"""\\1"""', content)

with open('tests/test_multi_framework_integration.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed docstrings")
