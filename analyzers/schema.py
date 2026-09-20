import os

def analyze(devkit_dir):
    schema_path = os.path.join(devkit_dir, "db", "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return "Schema file not found."
