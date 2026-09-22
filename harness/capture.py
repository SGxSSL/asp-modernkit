import urllib.request
import urllib.parse
import http.cookiejar
import os
import hashlib
import re

import yaml
import sys

# Config
AKIT_YAML = r"d:\Sonata\asp\asp-modernkit\akit.yaml"
GOLDENS_DIR = r"d:\Sonata\asp\asp-modernkit\harness\goldens"

def load_config():
    with open(AKIT_YAML, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()
harness_cfg = config.get("harness", {})
BASE_URL = harness_cfg.get("legacy_url", "http://localhost/cms")

ENDPOINTS = []
for slice_name, slice_data in config.get("slices", {}).items():
    for ep in slice_data.get("endpoints", []):
        if not ep.startswith("/"):
            ep = "/" + ep
        ENDPOINTS.append(ep)

# De-duplicate endpoints
ENDPOINTS = list(set(ENDPOINTS))


def normalize_html(html):
    """
    Removes highly volatile data like timestamps, CSRF tokens, 
    or random IDs to ensure deterministic baseline comparisons.
    """
    # Example: remove any hidden input fields that might contain random tokens
    # html = re.sub(r'<input type="hidden" name="token" value="[^"]+">', '<input type="hidden" name="token" value="NORMALIZED">', html)
    
    # Example: remove IIS debug timestamps if any exist in the footer
    # html = re.sub(r'Generated on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'Generated on [TIMESTAMP]', html)
    
    return html

def main():
    if not os.path.exists(GOLDENS_DIR):
        os.makedirs(GOLDENS_DIR)
        
    # Setup cookie jar to maintain session state across requests (e.g., ASPSESSIONID)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)

    success_count = 0

    print("Starting Golden Trace Capture...")
    
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        
        try:
            req = urllib.request.Request(url)
            # Add a typical User-Agent so we don't get blocked by simple filters
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ASP-Modernizer-Bot')
            
            with urllib.request.urlopen(req) as response:
                status = response.getcode()
                body = response.read().decode('utf-8', errors='replace')
                
        except urllib.error.HTTPError as e:
            # We still want to capture expected errors (like 403 Forbidden or 500s if they are part of the baseline)
            status = e.code
            body = e.read().decode('utf-8', errors='replace')
        except urllib.error.URLError as e:
            print(f"FAILED TO CONNECT to {url}: {e.reason}")
            continue
            
        # Normalize the body to remove random dynamic elements
        normalized_body = normalize_html(body)
        
        # Create a safe filename using a hash of the endpoint name
        safe_name = endpoint.replace('/', '_').replace('.', '_').strip('_')
        if not safe_name:
            safe_name = "index"
            
        filename = f"{safe_name}.txt"
        filepath = os.path.join(GOLDENS_DIR, filename)
        
        # We store the status code at the top, followed by the response body
        capture_content = f"STATUS: {status}\n---\n{normalized_body}"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(capture_content)
            
        success_count += 1
        print(f"Captured {url} -> {filename} (Status: {status})")
        
    print(f"\nCapture complete! {success_count}/{len(ENDPOINTS)} endpoints recorded.")

if __name__ == "__main__":
    main()
