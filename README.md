# ASP Modernization Devkit (asp-modernkit)

**asp-modernkit** is an autonomous, AI-driven orchestration engine designed to analyze, slice, and modernize massive, monolithic Classic ASP (VBScript) codebases into secure, production-ready **.NET 10 Web APIs** and **React TypeScript** frontends. 

It eliminates the need for manual, line-by-line translation by acting as an automated migration factory.

---

## 🏗️ Architecture & Directory Structure

To help you navigate the codebase, here is a detailed breakdown of why every file and folder exists and how they work together to modernize legacy code.

### Core Orchestration (`cli/` & `analyzers/`)
The core orchestrator is written entirely in Python and requires zero external compilers.
- `cli/akit.py`: The main entry point and CLI runner. Orchestrates the `facts`, `spec`, `plan`, and `gen` commands.
- `cli/bundler.py`: Traces legacy `#include` directives and packages a slice of files into a single context payload.
- `cli/llm.py`: Interfaces with the OpenRouter API, managing LLM context windows and JSON parsing.
- `analyzers/`: Contains the static analysis modules (Regex/AST) that extract VBScript routes, deadcode, session state logic, and SQL dialects without needing to execute the legacy code.

### Validation & Testing (`harness/` & `goldens/`)
- `harness/`: This directory contains our automated test harness scripts (`capture.py`, `db_build.py`).
- **`harness/goldens/`**: (Golden Master Testing). This folder stores the exact HTML/JSON responses produced by the *legacy* ASP application. When the new .NET/React application is generated, we run tests against these "golden" files to mathematically prove that the modernized app produces the exact same data and behavior as the legacy monolith!

### Data & Architecture (`db/` & `templates/`)
- `db/`: Contains the database schema migrations (`schema.sql`, `seed.sql`) and SQLite stubs used to port the legacy Access/SQL Server database into the modern Entity Framework Core environment.
- `templates/`: Contains the skeletal boilerplates (`backend-dotnet-clean`, `frontend-react-ts`). The LLM uses these templates as the architectural foundation when generating the new source code.
- `models/`: Stores `models.yaml`, configuring which LLMs (e.g., GPT-4o, Claude 3.5) are authorized for use in the Devkit.

### Configuration (`akit.yaml`)
- `akit.yaml`: The central configuration file. This is where you map your legacy repository and manually define logical "slices" (e.g., `admin_auth`, `public_catalog`) by listing their top-level `.asp` entry points. The orchestrator uses this to break the monolith into digestible chunks for the AI.

### Working Directories (Generated at Runtime)
These folders act as caches and logs dynamically populated during the migration pipeline:
- `bundles/`: Caches the aggregated JSON payload representing a specific slice (e.g., `admin_crud.json`) before it is sent to the LLM.
- `docs/`: Stores permanent, human-authored documentation (`RUNBOOK.md`, `HOWTO_akit_yaml.md`).
- `generated_docs/`: Automatically stores the AI-generated intermediate architectural designs and planning checklists (`SPEC_*.md`, `PLAN_*.md`, and raw LLM outputs).
- `prompts/`: A temporary storage cache for the highly-optimized text prompts right before they are dispatched to the LLM. 
- `telemetry/`: Contains `token_ledger.json`, which tracks your LLM token usage and calculates the real-time financial cost of running the AI models.

### Output Destination
- When code generation is complete, the devkit automatically scaffolds new directories at the root (e.g., `output_admin_crud/`). Inside, you will find fully containerized `backend/` (.NET) and `frontend/` (React) repositories that are ready to compile and run.

---

## 🚀 Runbook: Getting Started

### 1. Prerequisites
- **Python 3.10+**: Required to run the orchestrator.
- **Node.js**: Required to compile the generated React frontend.
- **.NET SDK (10.0+)**: Required to build the generated C# Web API.

### 2. Environment Setup
Before running the pipeline, set your OpenRouter API key in your terminal to authenticate with the LLMs:
```powershell
$env:OPENROUTER_API_KEY="sk-or-your-api-key"
```

### 3. The Migration Pipeline

**Step 1: Facts Extraction**
Point the static analyzer at your legacy Classic ASP repository to extract the architecture, file includes, and SQL dependencies into `facts.json`.
```bash
python cli/akit.py facts --source "C:\path\to\legacy\repo" --out facts.json
```

**Step 2: Define Slices in `akit.yaml`**
Open `akit.yaml` and define the slices (groups of legacy endpoints) that you want to modernize together. You only need to list the top-level files; the bundler will automatically pull in all nested dependencies!
```yaml
slices:
  my_new_slice:
    description: "Core module for processing orders"
    endpoints:
      - "orders/process.asp"
```

**Step 3: Architecture Spec Generation**
Run the AI orchestrator to dynamically design the modern C# Domain Models and API contracts based on the legacy slice.
```bash
python cli/akit.py spec my_new_slice
```

**Step 4: Implementation Plan Generation**
The AI will generate a granular, file-by-file Markdown checklist representing the new architecture.
```bash
python cli/akit.py plan my_new_slice
```

**Step 5: Code Generation**
Execute the mass-generation of the actual source code. The output will be parsed and saved to `output_my_new_slice/`.
```bash
python cli/akit.py gen my_new_slice
```

### 4. Test Harness (Golden Master & Database Export)
The Devkit includes a universal test harness to automatically dump the legacy database and capture "Golden Master" HTTP traces.

**Run the Golden Trace capture:**
```bash
python cli/akit.py capture
```
**Run the DB extraction:**
```bash
python cli/akit.py db build
```

> [!WARNING]
> **Requirements & Limitations for the Test Harness:**
> To use `capture` and `db build` on a new project, the following conditions must be met:
> 
> **Requirements:**
> 1. **Live Environment:** The legacy ASP application MUST be running locally (via IIS or IIS Express) and accessible at the `legacy_url` defined in your `akit.yaml`.
> 2. **Write Permissions (`db build`):** You must have file write permissions to the `public_dir` defined in `akit.yaml`, as the orchestrator needs to temporarily drop the `export.asp` script into the legacy web root.
> 3. **Database Compatibility (`db build`):** The legacy database must use standard ADO/OLE DB connections. `export.asp` relies on `Connection.OpenSchema` to dynamically extract table metadata.
> 
> **Limitations:**
> 1. **GET-Only Capture (`capture`):** The automated capture script only executes HTTP `GET` requests against your defined endpoints. It does not automatically crawl or submit `<form>` POST data.
> 2. **Authentication State (`capture`):** If an endpoint requires an active session (e.g. an Admin portal), the capture script will simply record the "403 Forbidden" or "302 Redirect to Login" response. If you want to capture the authenticated HTML, you will need to manually mock a session cookie inside `harness/capture.py`.
> 3. **Memory Limits (`db build`):** Because `export.asp` dumps the legacy database into a single JSON response, it works flawlessly for Microsoft Access databases, but may hit IIS memory/timeout limits if run against massive, multi-gigabyte SQL Server databases.

### 5. Cost Reporting
To view exactly how many tokens the AI consumed and the estimated cost across all your generation runs, use the reporting command:
```bash
python cli/akit.py report
```
