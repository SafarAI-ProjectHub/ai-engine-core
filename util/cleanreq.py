# dedup_requirements.py
seen = set()
with open(r'ai-engine-core/requirements.txt', 'r') as f:
    lines = f.readlines()

with open(r'ai-engine-core/clean_requirements.txt', 'w') as f:
    for line in lines:
        package = line.strip()
        if package and package not in seen:
            seen.add(package)
            f.write(package + '\n')