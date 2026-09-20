import re

def analyze(content):
    access_patterns = [
        r'(db\.getRecordSet\s*\(.*?\))',
        r'(db\.execute\s*\(.*?\))',
        r'(Server\.CreateObject\s*\(\s*"ADODB\.(Connection|Recordset)"\s*\))',
        r'(conn\.Execute\s*\(.*?\))'
    ]
    results = []
    for pattern in access_patterns:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            results.append(m.group(1))
    return list(set(results))
