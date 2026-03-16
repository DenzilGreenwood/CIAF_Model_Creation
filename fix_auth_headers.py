import re

with open('tests/test_vault_api_real.py', 'r') as f:
    content = f.read()

# Replace all X-API-Key headers with Authorization headers
content = content.replace('"X-API-Key": "valid_key"', '"Authorization": "Bearer valid_key"')

with open('tests/test_vault_api_real.py', 'w') as f:
    f.write(content)

print("Replaced all X-API-Key headers with Authorization: Bearer headers")
