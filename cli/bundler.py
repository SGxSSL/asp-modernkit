import os
import json

class Bundler:
    def __init__(self, devkit_root):
        self.devkit_root = devkit_root
        self.yaml_path = os.path.join(devkit_root, 'akit.yaml')
        self.facts_path = os.path.join(devkit_root, 'facts.json')
        self.config = self._parse_yaml()
        self.facts = self._load_facts()
        
    def _parse_yaml(self):
        """Naive stdlib-only YAML parser specific to akit.yaml structure."""
        data = {"slices": {}}
        current_slice = None
        
        if not os.path.exists(self.yaml_path):
            raise FileNotFoundError(f"Missing {self.yaml_path}")
            
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'): continue
                
                if stripped.startswith('legacy_root:'):
                    data["legacy_root"] = stripped.split(':', 1)[1].strip(' "')
                elif stripped.startswith('endpoints:') or not stripped.startswith('- '):
                    # We are in the slices block, but wait, the structure is:
                    # public_read:
                    pass
                if line.startswith('  ') and not line.startswith('    ') and stripped.endswith(':'):
                    # We are in the slices block
                    current_slice = stripped[:-1]
                    data["slices"][current_slice] = {"endpoints": []}
                elif stripped.startswith('- '):
                    if current_slice:
                        endpoint = stripped.split('- ', 1)[1].strip(' "')
                        data["slices"][current_slice]["endpoints"].append(endpoint)
                        
        return data

    def _load_facts(self):
        if not os.path.exists(self.facts_path):
            raise FileNotFoundError(f"Missing {self.facts_path}. Run 'akit facts' first.")
        with open(self.facts_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def resolve_slice_dependencies(self, slice_name):
        """Walk the include graph to find all files needed for this slice."""
        if slice_name not in self.config["slices"]:
            raise ValueError(f"Slice '{slice_name}' not defined in akit.yaml")
            
        endpoints = self.config["slices"][slice_name]["endpoints"]
        includes_graph = self.facts.get("includes", {})
        
        visited = set()
        queue = list(endpoints)
        
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                if current in includes_graph:
                    queue.extend(includes_graph[current])
                    
        return list(visited)

    def generate_bundle(self, slice_name):
        """Construct the LLM context bundle for a specific slice."""
        files_needed = self.resolve_slice_dependencies(slice_name)
        legacy_root = self.config.get("legacy_root")
        
        if not legacy_root or not os.path.isdir(legacy_root):
            raise ValueError("Invalid legacy_root in akit.yaml")
            
        bundle = {
            "slice": slice_name,
            "endpoints": self.config["slices"][slice_name]["endpoints"],
            "schema": self.facts.get("schema", ""),
            "files": {}
        }
        
        # Gather source code and facts for the resolved files
        for f in files_needed:
            abs_path = os.path.normpath(os.path.join(legacy_root, f))
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    code = fp.read()
                    
                bundle["files"][f] = {
                    "source": code,
                    "data_access": self.facts.get("data_access", {}).get(f, []),
                    "sql_dialect": self.facts.get("sql_dialect", {}).get(f, []),
                    "session_state": self.facts.get("session_state", {}).get(f, [])
                }
            except Exception as e:
                bundle["files"][f] = {"error": str(e)}
                
        return bundle

# For internal testing/verification
if __name__ == "__main__":
    devkit = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    b = Bundler(devkit)
    print("Testing Slice Resolution: public_read")
    deps = b.resolve_slice_dependencies("public_read")
    print(f"Files required: {len(deps)}")
    for d in deps:
        print(f"  - {d}")
