# P1 Facts Summary
**Objective:** Replace subjective human estimation with deterministic static analysis by parsing the legacy codebase to build a structured map (`facts.json`) containing exactly zero parse failures.

## 1. The Devkit CLI (`akit.py`)
To manage the modernization pipeline, we initialized the primary orchestration CLI: `akit`.
* **The Architecture:** The tool uses Python 3.12 (standard library only) ensuring it can run in restricted, no-admin environments.
* **Command Structure:** The CLI uses `argparse` with subcommands explicitly mapped to the project spec (e.g., `scan`, `graph`, `facts`, `db build`, `capture`, `gen`, `verify`).

## 2. Decoupled Static Analyzers
We built 8 distinct, decoupled static analyzers located in the `analyzers/` module. These perform deep parsing of the Classic ASP codebase without ever actually executing the VBScript.

1. **Inventory (`inventory.py`)**: Traverses the legacy source and outputs a normalized, relative-path list of all 687 files.
2. **Includes (`includes.py`)**: Parses `<!--#include file="..." -->` directives using regex to build a robust dependency graph connecting 83 files (e.g., how library files hook into endpoints).
3. **Routes (`routes.py`)**: Differentiates true HTTP entry-points (130 `.asp` files in `public/`) from partial templates or included logic.
4. **Data Access (`data_access.py`)**: Locates exactly where the code touches the database (e.g., `db.getRecordSet`) across 55 files.
5. **SQL Dialect (`sql_dialect.py`)**: Extracts raw SQL string assignments across 45 files to give the LLM context into the specific Access SQL dialects used.
6. **Session State (`session_state.py`)**: Maps out authentication and state boundaries by finding all reads/writes to the `Session` object across 13 files.
7. **Deadcode (`deadcode.py`)**: Performs a graph traversal (starting from Routes, navigating through Includes) against the total Inventory. It successfully identified 42 orphaned, unreachable files that can be entirely ignored during the rewrite.
8. **Schema (`schema.py`)**: Injects the modernized SQLite `schema.sql` (generated in P0) directly into the facts bundle.

## 3. Structural Realignment
We enforced strict adherence to the project specification by building out the exact required directory scaffold:
* Created directories for `prompts/`, `schemas/`, `templates/backend-dotnet-clean/`, `templates/frontend-react-ts/`, `models/`, `telemetry/`, and `.github/`.
* Created configuration stubs: `akit.yaml`, `models/models.yaml`, `telemetry/ledger.csv`, and `docs/RUNBOOK.md`.

> **Status:** All P1 Exit Gates have been met. The analyzers successfully extracted deep contextual facts, generated a unified `facts.json` payload, and hit exactly **zero parse failures**. We are fully prepared to move to **P2 (Bundles)**.
