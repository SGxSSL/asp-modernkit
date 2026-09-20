import urllib.request
import json
import sqlite3
import shutil
import os
import datetime

# Config
BASE_URL = "http://localhost/cms/export.asp"
PUBLIC_DIR = r"d:\Sonata\asp\asp-vbscript-cms\public"
EXPORT_SCRIPT = r"d:\Sonata\asp\asp-modernkit\harness\export.asp"
DB_DIR = r"d:\Sonata\asp\asp-modernkit\db"

def map_type(ado_type, is_first_col):
    """Maps MS Access ADO types to SQLite types."""
    # 3 = Integer
    if ado_type == 3:
        return "INTEGER PRIMARY KEY AUTOINCREMENT" if is_first_col else "INTEGER"
    # 2 = SmallInt, 17 = TinyInt
    elif ado_type in (2, 17):
        return "INTEGER"
    # 11 = Boolean
    elif ado_type == 11:
        return "INTEGER"
    # 7, 133, 135 = Date/Time
    elif ado_type in (7, 133, 135):
        return "TEXT"
    # 130, 202, 203 = Text/Memo
    elif ado_type in (130, 202, 203):
        return "TEXT"
    # 6 = Currency
    elif ado_type == 6:
        return "INTEGER"
    # 4 = Single, 5 = Double, 131 = Numeric
    elif ado_type in (4, 5, 131):
        return "REAL"
    else:
        return "TEXT" # Fallback

def format_value(val, ado_type):
    if val is None:
        return "NULL"
    
    # Boolean
    if ado_type == 11:
        if isinstance(val, bool):
            return "1" if val else "0"
        if str(val).lower() in ("true", "1", "yes", "-1"):
            return "1"
        return "0"
    
    # Currency (convert to cents)
    if ado_type == 6:
        try:
            return str(int(float(val) * 100))
        except:
            return "0"

    # Date
    if ado_type in (7, 133, 135):
        # Format as ISO if possible, otherwise string literal
        return f"'{str(val)}'"

    # Number
    if ado_type in (2, 3, 17, 4, 5, 131):
        return str(val)

    # String (escape single quotes)
    safe_str = str(val).replace("'", "''")
    return f"'{safe_str}'"

def generate_sql(db_json):
    schema_sql = []
    seed_sql = []
    
    for table in db_json.get("tables", []):
        t_name = table["name"]
        cols = table.get("columns", [])
        rows = table.get("rows", [])
        
        # Build Schema
        schema_sql.append(f"CREATE TABLE [{t_name}] (")
        col_defs = []
        for idx, col in enumerate(cols):
            c_name = col["name"]
            c_type = map_type(col["type"], is_first_col=(idx == 0))
            col_defs.append(f"    [{c_name}] {c_type}")
        schema_sql.append(",\n".join(col_defs))
        schema_sql.append(");\n")
        
        # Build Seed
        if rows:
            col_names = [f"[{c['name']}]" for c in cols]
            for row in rows:
                vals = []
                for col in cols:
                    val = row.get(col["name"])
                    vals.append(format_value(val, col["type"]))
                
                seed_sql.append(f"INSERT INTO [{t_name}] ({', '.join(col_names)}) VALUES ({', '.join(vals)});")
            seed_sql.append("") # newline
            
    return "\n".join(schema_sql), "\n".join(seed_sql)

def main():
    dest = os.path.join(PUBLIC_DIR, "export.asp")
    print(f"Dropping {dest}...")
    shutil.copy(EXPORT_SCRIPT, dest)

    try:
        print("Fetching data from Access via HTTP...")
        req = urllib.request.Request(BASE_URL)
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8', errors='replace')
        
        db_json = json.loads(data)
        out_json = os.path.join(DB_DIR, "export.json")
        with open(out_json, "w", encoding='utf-8') as f:
            json.dump(db_json, f, indent=2)
        print(f"Successfully exported JSON to {out_json}")
        
        # Generate SQL
        schema_str, seed_str = generate_sql(db_json)
        
        schema_file = os.path.join(DB_DIR, "schema.sql")
        seed_file = os.path.join(DB_DIR, "seed.sql")
        sqlite_file = os.path.join(DB_DIR, "cms.sqlite")
        
        with open(schema_file, "w", encoding='utf-8') as f:
            f.write(schema_str)
        with open(seed_file, "w", encoding='utf-8') as f:
            f.write(seed_str)
            
        print(f"Generated {schema_file} and {seed_file}")
        
        # Execute into SQLite
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)
            
        print(f"Building SQLite database {sqlite_file}...")
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        # Execute Schema
        cursor.executescript(schema_str)
        
        # Execute Seed
        cursor.executescript(seed_str)
        
        conn.commit()
        conn.close()
        print("Database successfully built!")

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if os.path.exists(dest):
            os.remove(dest)
            print("Cleaned up export.asp")

if __name__ == "__main__":
    main()
