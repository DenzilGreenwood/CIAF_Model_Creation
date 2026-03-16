with open('ciaf/vault/api.py', 'r') as f:
    content = f.read()

# Fix all occurrences of client_request.client.host access
old_pattern = 'ip_address=client_request.client.host if client_request else None'
new_pattern = 'ip_address=client_request.client.host if (client_request and client_request.client) else None'

content = content.replace(old_pattern, new_pattern)

with open('ciaf/vault/api.py', 'w') as f:
    f.write(content)

print(f"Fixed client_request.client.host access patterns for testability")
