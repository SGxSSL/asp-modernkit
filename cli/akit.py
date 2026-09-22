import argparse
import sys
import json
import os
import re

# Ensure the devkit root is in the Python path so we can import modules
devkit_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, devkit_root)

from analyzers import inventory, includes, routes, data_access, sql_dialect, session_state, schema, deadcode
import bundler
import llm

def ensure_dirs():
    dirs = ['docs', 'prompts', 'bundles']
    for d in dirs:
        path = os.path.join(devkit_root, d)
        os.makedirs(path, exist_ok=True)

def normalize_path(path, source_dir):
    try:
        rel = os.path.relpath(path, source_dir)
        return rel.replace("\\", "/")
    except ValueError:
        return path

def cmd_facts(args):
    source = os.path.abspath(args.source)
    if not os.path.isdir(source):
        print(f"Error: Source directory '{source}' does not exist.")
        sys.exit(1)
        
    print(f"Analyzing {source}...")
    
    inv = inventory.analyze(source, normalize_path)
    inc_map = {}
    routes_list = []
    da_map = {}
    sql_map = {}
    session_map = {}
    
    for f in inv:
        abs_path = os.path.normpath(os.path.join(source, f))
        
        if f.lower().endswith(('.asp', '.inc')):
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    
                inc = includes.analyze(abs_path, content, source, normalize_path)
                if inc: inc_map[f] = inc
                
                da = data_access.analyze(content)
                if da: da_map[f] = da
                
                sq = sql_dialect.analyze(content)
                if sq: sql_map[f] = sq
                
                sess = session_state.analyze(content)
                if sess: session_map[f] = sess
            except Exception as e:
                print(f"Error parsing {f}: {e}")
                
        if routes.analyze(f):
            routes_list.append(f)
            
    dc = deadcode.analyze(inv, routes_list, inc_map)
    sch = schema.analyze(devkit_root)
    
    facts = {
        "inventory": inv,
        "includes": inc_map,
        "routes": routes_list,
        "data_access": da_map,
        "sql_dialect": sql_map,
        "session_state": session_map,
        "deadcode": dc,
        "schema": sch
    }
    
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    with open(args.out, "w", encoding="utf-8") as fp:
        json.dump(facts, fp, indent=2)
        
    print(f"Facts successfully extracted to {args.out}")

def cmd_spec(args):
    ensure_dirs()
    b = bundler.Bundler(devkit_root)
    print(f"Generating bundle for slice '{args.slice}'...")
    bundle = b.generate_bundle(args.slice)
    
    prompt = f"""You are modernizing a legacy Classic ASP application to .NET 10 (backend) and React TS (frontend).
Please generate an Architectural Specification for the slice '{args.slice}'.

Include:
1. Domain Model (Entities, based on the DB schema and data access usage)
2. OpenAPI Specification drafts for the new backend APIs that will replace the legacy endpoints.
3. Architecture Decision Records (ADRs) for migration strategies.

Here is the context bundle containing exactly the code for this slice:
{json.dumps(bundle, indent=2)}
"""
    prompt_path = os.path.join(devkit_root, 'prompts', f'spec_{args.slice}.txt')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print(f"Saved optimized prompt to {prompt_path}")
    
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        print("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is set. Skipping LLM execution. You can manually run the prompt.")
        return
        
    print("Calling LLM (this may take a minute)...")
    try:
        spec = llm.generate_completion(prompt)
        out_path = os.path.join(devkit_root, 'docs', f'SPEC_{args.slice}.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(spec)
        print(f"Spec successfully generated at {out_path}")
    except Exception as e:
        print(f"LLM Error: {e}")

def cmd_plan(args):
    ensure_dirs()
    b = bundler.Bundler(devkit_root)
    print(f"Generating bundle for slice '{args.slice}'...")
    bundle = b.generate_bundle(args.slice)
    
    spec_path = os.path.join(devkit_root, 'docs', f'SPEC_{args.slice}.md')
    spec_content = "Spec not found. Proceeding without architectural spec."
    if os.path.exists(spec_path):
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
            
    prompt = f"""You are modernizing a legacy Classic ASP application to .NET 10 (backend) and React TS (frontend).
Please generate a granular, file-by-file Task List for the slice '{args.slice}'.
Format it as a markdown checklist (e.g. - [ ] Task name).

CRITICAL INSTRUCTION: You MUST include tasks to generate the necessary project configuration files, such as `frontend/package.json`, `frontend/tsconfig.json`, and `backend/backend.csproj`. The code cannot run without these.

Here is the Architectural Spec:
{spec_content}

Here is the legacy context bundle:
{json.dumps(bundle, indent=2)}
"""
    prompt_path = os.path.join(devkit_root, 'prompts', f'plan_{args.slice}.txt')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print(f"Saved optimized prompt to {prompt_path}")
    
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        print("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is set. Skipping LLM execution. You can manually run the prompt.")
        return
        
    print("Calling LLM (this may take a minute)...")
    try:
        plan = llm.generate_completion(prompt)
        out_path = os.path.join(devkit_root, 'docs', f'PLAN_{args.slice}.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(plan)
        print(f"Plan successfully generated at {out_path}")
    except Exception as e:
        print(f"LLM Error: {e}")

def cmd_gen(args):
    ensure_dirs()
    b = bundler.Bundler(devkit_root)
    print(f"Generating bundle for slice '{args.slice}'...")
    bundle = b.generate_bundle(args.slice)
    
    spec_path = os.path.join(devkit_root, 'docs', f'SPEC_{args.slice}.md')
    plan_path = os.path.join(devkit_root, 'docs', f'PLAN_{args.slice}.md')
    
    spec_content = open(spec_path, 'r', encoding='utf-8').read() if os.path.exists(spec_path) else "No Spec."
    plan_content = open(plan_path, 'r', encoding='utf-8').read() if os.path.exists(plan_path) else "No Plan."

    prompt = f"""You are executing a modernization from Classic ASP to .NET 10 and React TS for the slice '{args.slice}'.
Please write the fully functional source code for the backend and frontend components as defined in the Task List.

OUTPUT FORMAT INSTRUCTIONS:
You MUST output all generated code inside XML `<file>` tags. Do not use markdown code blocks for the files.
Provide the relative file path inside the `path` attribute. Prefix backend files with 'backend/' and frontend files with 'frontend/'.
CRITICAL: You MUST generate the `frontend/package.json` and `backend/*.csproj` files if they are in the task list.

SECURITY DIRECTIVES (CRITICAL):
1. All database access MUST use Entity Framework Core LINQ or parameterized SQL. Do NOT concatenate strings for SQL queries.
2. Ensure 100% validation parity with the legacy VBScript validation logic.
3. Do NOT hardcode any secrets, passwords, or connection strings in the source code. Read them from configuration/appsettings.

Example:
<file path="backend/Controllers/ExampleController.cs">
using System;
...
</file>

<file path="frontend/src/App.tsx">
import React from 'react';
...
</file>

Here is the Architectural Spec:
{spec_content}

Here is the Task List:
{plan_content}

Here is the legacy context bundle:
{json.dumps(bundle, indent=2)}

Begin generating the files now using exactly the requested XML format.
"""
    prompt_path = os.path.join(devkit_root, 'prompts', f'gen_{args.slice}.txt')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print(f"Saved optimized prompt to {prompt_path}")
    
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY"):
        print("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is set. Skipping LLM execution. You can manually run the prompt.")
        return
        
    print("Calling LLM to generate code (this will take a while)...")
    try:
        output = llm.generate_completion(prompt)
        
        # Save raw output for debugging
        raw_out_path = os.path.join(devkit_root, 'docs', f'GEN_RAW_{args.slice}.md')
        with open(raw_out_path, 'w', encoding='utf-8') as f:
            f.write(output)
            
        print("Parsing XML output to extract files...")
        out_dir = os.path.join(devkit_root, f'output_{args.slice}')
        
        # Regex to find <file path="...">content</file>
        pattern = re.compile(r'<file\s+path="([^"]+)">([\s\S]*?)</file>', re.IGNORECASE)
        matches = pattern.findall(output)
        
        if not matches:
            print("Warning: No <file> tags found in LLM output. Check GEN_RAW document.")
            return
            
        for path, content in matches:
            full_path = os.path.normpath(os.path.join(out_dir, path))
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Clean up potential CDATA wrapping hallucinated by the LLM
            clean_content = content.strip()
            if clean_content.startswith('<![CDATA['):
                clean_content = clean_content[9:]
            if clean_content.endswith(']]>'):
                clean_content = clean_content[:-3]
                
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(clean_content.strip() + '\n')
            print(f"Created: {path}")
            
        print(f"Code generation complete! Files saved to: {out_dir}")
    except Exception as e:
        print(f"LLM Error: {e}")

def cmd_report(args):
    ledger_path = os.path.join(devkit_root, 'docs', 'token_ledger.json')
    if not os.path.exists(ledger_path):
        print("No token ledger found. Run generation commands first.")
        return
        
    try:
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
            
        total_prompt = sum(entry.get('prompt_tokens', 0) for entry in ledger)
        total_completion = sum(entry.get('completion_tokens', 0) for entry in ledger)
        total = total_prompt + total_completion
        
        # OpenRouter/free is free, but let's calculate what it would cost on a standard model (e.g. gpt-4o-mini)
        # Assuming $0.15 / 1M input tokens and $0.60 / 1M output tokens for a cheap fast model
        cost_prompt = (total_prompt / 1_000_000) * 0.15
        cost_completion = (total_completion / 1_000_000) * 0.60
        total_cost = cost_prompt + cost_completion
        
        print("\n=== AI Orchestration Cost Report ===")
        print(f"Total API Calls:     {len(ledger)}")
        print(f"Prompt Tokens:       {total_prompt:,}")
        print(f"Completion Tokens:   {total_completion:,}")
        print(f"Total Tokens:        {total:,}")
        print("------------------------------------")
        print(f"Estimated Cost (if using paid fast model): ${total_cost:.4f}")
        print("====================================\n")
    except Exception as e:
        print(f"Error reading ledger: {e}")

import subprocess

def cmd_capture(args):
    script_path = os.path.join(devkit_root, 'harness', 'capture.py')
    print("Running Golden Trace Capture...")
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running capture.py: {e}")

def cmd_db(args):
    if args.db_command == "build":
        script_path = os.path.join(devkit_root, 'harness', 'db_build.py')
        print("Running Database Export and SQLite Build...")
        try:
            subprocess.run([sys.executable, script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running db_build.py: {e}")
    else:
        print("Usage: akit db build")

def main():
    parser = argparse.ArgumentParser(description="ASP Modernization Devkit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    subparsers.add_parser("scan", help="inventory + LOC + encodings")
    subparsers.add_parser("graph", help="include/call graph -> Mermaid")
    
    facts_parser = subparsers.add_parser("facts", help="all analyzers -> facts.json")
    facts_parser.add_argument("--source", required=True, help="Path to the legacy ASP repository")
    facts_parser.add_argument("--out", required=True, help="Path to save the facts.json file")
    
    subparsers.add_parser("export", help="dump legacy schema + data via the app")
    
    db_parser = subparsers.add_parser("db", help="Database commands")
    db_subparsers = db_parser.add_subparsers(dest="db_command")
    db_subparsers.add_parser("build", help="build cms.sqlite + SQL artifacts")
    
    subparsers.add_parser("capture", help="record golden traces")
    subparsers.add_parser("summarize", help="per-page behaviour summaries")
    
    spec_parser = subparsers.add_parser("spec", help="domain model + OpenAPI + ADR drafts")
    spec_parser.add_argument("slice", help="The name of the slice (e.g. public_read)")
    
    plan_parser = subparsers.add_parser("plan", help="slice -> task list")
    plan_parser.add_argument("slice", help="The name of the slice (e.g. public_read)")
    
    gen_parser = subparsers.add_parser("gen", help="generate backend/frontend for a slice")
    gen_parser.add_argument("slice", help="Name of the slice to generate")
    
    subparsers.add_parser("verify", help="replay + tests + parity report")
    subparsers.add_parser("report", help="parity + token/cost summary")

    args = parser.parse_args()
    
    if args.command == "facts":
        cmd_facts(args)
    elif args.command == "spec":
        cmd_spec(args)
    elif args.command == "plan":
        cmd_plan(args)
    elif args.command == "gen":
        cmd_gen(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "capture":
        cmd_capture(args)
    elif args.command == "db":
        cmd_db(args)
    elif args.command:
        print(f"Command '{args.command}' is scaffolded but not yet implemented.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
