#!/usr/bin/env python3
"""Find all triple-quote positions in a file"""

with open('ciaf/industries/biotechnology.py', 'r', encoding='utf-8') as f:
    content = f.read()
    count = 0
    pos = 0
    quotes = []
    while True:
        idx = content.find('"""', pos)
        if idx == -1:
            break
        count += 1
        # Find line number
        line_num = content[:idx].count('\n') + 1
        quotes.append(line_num)
        print(f'{count}: Line {line_num}')
        pos = idx + 3
    print(f'\nTotal: {count}')
    if count % 2 == 1:
        print(f'\nODD NUMBER! Unclosed string likely near line {quotes[-1]}')
