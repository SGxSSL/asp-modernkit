def analyze(rel_path):
    if rel_path.endswith('.asp') and rel_path.startswith("public/"):
        if not ("/include/" in rel_path or "/inc/" in rel_path):
            return True
    return False
