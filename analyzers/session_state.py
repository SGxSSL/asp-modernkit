import re

def analyze(content):
    pattern = re.compile(r'Session\s*\(\s*"([^"]+)"\s*\)', re.IGNORECASE)
    results = []
    for m in pattern.finditer(content):
        results.append(m.group(1))
    return list(set(results))
