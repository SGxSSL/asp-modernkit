import os

def analyze(source_dir, normalize_path):
    inventory = []
    for root, _, files in os.walk(source_dir):
        if ".git" in root.split(os.sep): continue
        for file in files:
            abs_path = os.path.join(root, file)
            inventory.append(normalize_path(abs_path, source_dir))
    return inventory
