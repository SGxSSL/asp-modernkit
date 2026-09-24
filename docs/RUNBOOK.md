# ASP Modernization Devkit: Runbook

This runbook provides step-by-step instructions on how to operate the `asp-modernkit` orchestration engine. 

## 1. Prerequisites
- **Python 3.10+**: Must be installed on your system.
- **Node.js**: Required to compile and run the generated React frontend.
- **.NET SDK (10.0+)**: Required to compile and run the generated C# Web API.
- **OpenRouter API Key**: Set as an environment variable to authenticate with the LLMs.

## 2. Environment Setup
Before running the pipeline, set your API key in your terminal:
```powershell
$env:OPENROUTER_API_KEY="sk-or-your-api-key"
```

## 3. The Orchestration Pipeline

### Step 1: Test Harness (Optional)
Extract the "legacy database schema to SQLite and capture baseline "Golden Master" HTTP traces so you can validate the AI's future output.
*(Ensure your legacy application is running locally before executing these!)*
```bash
python cli/akit.py db build
python cli/akit.py capture
```

### Step 2: Facts Extraction
Point the static analyzer at your legacy Classic ASP repository to extract the architecture, includes, and SQL dependencies into `facts.json`.
```bash
python cli/akit.py facts --source "C:\path\to\legacy\repo" --out facts.json
```

### Step 3: Define Slices
Open `akit.yaml` and define logical "slices" (groups of legacy endpoints) that you want to modernize together.
```yaml
slices:
  my_new_slice:
    description: "Core module for processing orders"
    endpoints:
      - "orders/process.asp"
```

### Step 4: Architecture Spec Generation
Run the AI orchestrator to design the C# Domain Models and API contracts based on the legacy slice.
```bash
python cli/akit.py spec my_new_slice
```

### Step 5: Implementation Plan Generation
Generate the granular `.cs` and `.tsx` file checklist.
```bash
python cli/akit.py plan my_new_slice
```

### Step 6: Code Generation
Execute the mass-generation of the actual source code. The output will be saved to `output_my_new_slice/`.
```bash
python cli/akit.py gen my_new_slice
```

## 4. Reporting & Cost
To view exactly how many tokens the AI consumed and the estimated cost across all your generation runs, use the reporting command:
```bash
python cli/akit.py report
```

## 5. Troubleshooting
- **Missing Directories**: The Devkit automatically generates `docs/`, `prompts/`, and `bundles/` folders at runtime. If you encounter file path errors, ensure you have write permissions in the current working directory.
- **Empty Generated Output**: If the generated backend or frontend is missing actual business logic classes, the LLM likely hit its strict output token limit. Switch to a model with a larger max output window (e.g., `gpt-4o`) in `cli/llm.py`.
