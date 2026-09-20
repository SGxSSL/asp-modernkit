import re

def analyze(content):
    pattern = re.compile(r'"\s*(SELECT|INSERT INTO|UPDATE|DELETE FROM)\s+[^"]+"', re.IGNORECASE)
    results = []
    for m in pattern.finditer(content):
        results.append(m.group(0))
    return list(set(results))
