# P0 Baseline Summary
**Objective:** Prove that a Classic ASP application can be running, have its legacy database converted to a modern SQLite format without administrator rights, and capture deterministic "Golden" traces to serve as our regression baseline.

## 1. Database Extraction (`export.asp`)
Because we are operating in a strict no-admin environment, we could not install system-wide 64-bit ODBC drivers to access the legacy MS Access (`.mdb`) database.
To circumvent this, we created `export.asp`.
* **The Mechanism:** We temporarily dropped this VBScript file into the legacy app's `public/` root. Because the legacy app runs in a 32-bit IIS App Pool (which natively supports the Microsoft.Jet.OLEDB.4.0 driver), our script inherited the ability to read the database.
* **The Output:** The script dynamically queried `ADODB.Connection.OpenSchema` to fetch all tables, then looped through all rows, generating a massive, cleanly formatted JSON payload over HTTP.

## 2. SQLite Database Generation (`db_build.py`)
With the legacy data extracted as JSON, we needed to generate a modern SQLite database that the future .NET 10 rewrite will connect to.
* **The Mechanism:** We created a Python orchestrator (`db_build.py`) that first triggers the `export.asp` script over HTTP and saves the JSON. 
* **Type Mapping:** It programmatically converts legacy ADO data types to SQLite types (e.g., ADO Type 130 becomes `TEXT`, ADO Type 11 booleans become `INTEGER` 1/0). These rules are strictly documented in `db/mapping.md`.
* **The Output:** The script generates standard `schema.sql` (CREATE TABLE) and `seed.sql` (INSERT INTO) scripts, and then uses Python's built-in `sqlite3` library to execute them, resulting in a fully populated, standalone `cms.sqlite` database file.

## 3. Golden Trace Capture (`capture.py`)
To mathematically prove that our future .NET 10 / React rewrite achieves 100% parity with the legacy app, we must establish a deterministic baseline. Relying on humans to "eyeball" the UI is highly error-prone.
* **The Mechanism:** We created `capture.py`, which acts as an automated web scraper. It hits 20 predefined critical URLs (including public paths and admin CRUD paths). 
* **Normalization:** It strips out highly volatile data (like randomly generated timestamps) from the raw HTML to ensure the traces remain completely deterministic across multiple runs.
* **The Output:** 20 text files in `harness/goldens/` containing the exact HTTP Status Code and HTML body returned by the legacy application. During the rewrite phase, we will use an automated `diff` tool to compare the new .NET API's responses against these Golden files.

## 4. Legacy Bug Fixes
During the Golden Trace capture, we detected several fatal `HTTP 500` errors natively present in the legacy `jameswilson` repository. We surgically fixed these to ensure a valid baseline:
* **ASP 0141 (Page Command Repeated):** Removed a duplicate `<% @Language = VBScript %>` declaration in `bootstrap.asp` that was crashing the admin login.
* **Naming Collision:** Renamed the `DISABLED` constant in the logging library to `DEBUG_DISABLED` to prevent a collision with the forms library.
* **Option Explicit Violations:** Fixed undefined variables (`strDebugHTML` and `rsTestimonials`) in the Testimonials module that were causing hard crashes.

> **Status:** All P0 Exit Gates have been met. The legacy app is running, the database is successfully converted to SQLite, and 20 endpoints were captured twice with identical results. We are ready to proceed to **P1 (Facts)**.
