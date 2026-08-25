import os

total = 0
print(f"{'FILENAME':<42} | {'LINE COUNT':>12}")
print("-" * 58)

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'venv' in root:
        continue
    for file in sorted(files):
        if file.endswith(('.py', '.html', '.css', '.js')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total += lines
                    print(f"{file:<42} | {lines:>10} lines")
            except Exception as e:
                pass

print("-" * 58)
print(f"{'TOTAL CODEBASE LINES':<42} | {total:>10} lines")
