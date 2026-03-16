import json

with open('coverage.json') as f:
    data = json.load(f)

print(f"Total Coverage: {data['totals']['percent_covered']:.2f}%")
print(f"Statements: {data['totals']['num_statements']}")
print(f"Covered: {data['totals']['covered_lines']}")
print(f"Missing: {data['totals']['missing_lines']}")
print()
print("Key modules:")
print(f"  ciaf/core/merkle.py: {data['files']['ciaf\\core\\merkle.py']['summary']['percent_covered']:.1f}%")
print(f"  ciaf/api/framework.py: {data['files']['ciaf\\api\\framework.py']['summary']['percent_covered']:.1f}%")
print()
print("Verification services:")
vf = data['files'].get('ciaf\\verification\\verification_service.py', {})
ps = data['files'].get('ciaf\\verification\\proof_store.py', {})
if vf:
    print(f"  verification_service.py: {vf['summary']['percent_covered']:.1f}%")
if ps:
    print(f"  proof_store.py: {ps['summary']['percent_covered']:.1f}%")
