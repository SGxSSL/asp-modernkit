import os
import re

def analyze(abs_path, content, source_dir, normalize_path):
    includes = []
    
    # 1. Match standard SSI includes: <!--#include file="path"-->
    ssi_pattern = re.compile(r'<!--#include\s+(file|virtual)\s*=\s*"([^"]+)"\s*-->', re.IGNORECASE)
    for match in ssi_pattern.finditer(content):
        inc_type = match.group(1).lower()
        inc_path = match.group(2)
        if inc_type == "file":
            current_dir = os.path.dirname(abs_path)
            resolved = os.path.normpath(os.path.join(current_dir, inc_path))
        else:
            resolved = os.path.normpath(os.path.join(source_dir, inc_path.lstrip("/")))
        includes.append(normalize_path(resolved, source_dir))
        
    # 2. Match Server.Execute and Server.Transfer
    server_pattern = re.compile(r'Server\.(Execute|Transfer)\s*\(\s*"([^"]+)"\s*\)', re.IGNORECASE)
    for match in server_pattern.finditer(content):
        inc_path = match.group(2)
        # Server.Execute paths are generally relative to the current file or virtual. 
        # In this legacy app, they seem to be relative paths (e.g. "../core/include/application.asp")
        current_dir = os.path.dirname(abs_path)
        resolved = os.path.normpath(os.path.join(current_dir, inc_path))
        includes.append(normalize_path(resolved, source_dir))
        
    return list(set(includes))
