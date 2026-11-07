with open('vista/frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '3rd' in line.lower() or 'deep learning' in line.lower():
        print(f"{i+1}: {line.strip()}")
