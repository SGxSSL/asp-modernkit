# How to Configure `akit.yaml`

The `akit.yaml` file is the central configuration brain for the ASP Modernization Devkit. It tells the orchestrator where your legacy code lives and how to slice it up into manageable pieces for the AI to rewrite.

## 1. The Structure of `akit.yaml`

A valid `akit.yaml` file consists of three main sections: **Project Details**, **Targets**, and **Slices**.

```yaml
project:
  name: "Your Project Name"
  legacy_root: "C:/absolute/path/to/legacy/repo"
  db_engine: "sqlite" # or sqlserver, mysql, etc.
  
targets:
  backend: "backend-dotnet-clean"
  frontend: "frontend-react-ts"

slices:
  auth_module:
    description: "Handles user login and registration"
    endpoints:
      - "login.asp"
      - "register.asp"
      
  products_module:
    description: "Product catalog and detail pages"
    endpoints:
      - "catalog/list.asp"
      - "catalog/view.asp"
```

## 2. How to Manually Write Slices

When modernizing a massive legacy monolith, you cannot feed the entire repository to the AI at once. You must break it down into "Slices".

1. **Run the Facts Extractor**: First, run `python cli/akit.py facts` to generate the `facts.json` inventory.
2. **Identify Entry Points**: Look through the inventory and find the `.asp` files that represent the main screens or APIs of a specific feature (e.g., the Shopping Cart).
3. **Define the Slice**: Create a new key under `slices:` in the YAML file.
4. **Add Endpoints**: List the entry point `.asp` files under the `endpoints:` array. *Note: You only need to list the top-level files! The `bundler.py` will automatically read `facts.json` and recursively pull in all necessary `#include` files (like `db_connect.inc`).*

## 3. Future Roadmap: Automating `akit.yaml`

Currently, creating the YAML slices is a manual, human-driven architectural process. However, the Devkit is architected to support automated slicing in the future using one of these three approaches:

### A. AI-Powered Slicing (Recommended)
Because we already extract the entire codebase inventory into `facts.json`, we could implement an `akit auto-slice` command. This command would send the `facts.json` file to the LLM and ask it to intelligently group the files into logical business domains, returning a fully generated `akit.yaml` file automatically.

### B. Directory-Based Heuristics
We could build a script that simply assumes your folder structure matches your business logic. It would traverse the legacy repository and automatically generate a slice for every top-level directory (e.g., everything inside the `admin/` folder becomes the `admin_slice`).

### C. Graph Dependency Clustering
The `facts.json` file tracks every `#include` relationship. Using mathematical graph clustering (like the Louvain method via Python's `networkx` library), the Devkit could detect isolated clusters of files that heavily include each other and automatically bundle them into slices.
