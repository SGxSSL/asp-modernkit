# Access to SQLite Type Mapping

This document encodes our exact type mapping decisions for converting the legacy MS Access database to SQLite.

| Access Type | ADO Type Code | SQLite Type | Notes |
| :--- | :--- | :--- | :--- |
| AutoNumber / Integer | 3 | `INTEGER PRIMARY KEY AUTOINCREMENT` / `INTEGER` | The first column of a table, if it is an integer (Type 3), is assumed to be the AutoNumber Primary Key. Otherwise, mapped to standard `INTEGER`. |
| SmallInt | 2 | `INTEGER` | |
| Boolean (Yes/No) | 11 | `INTEGER` | SQLite doesn't have a boolean type. We map this to `1` (true/yes) or `0` (false/no). **Warning: highest-risk conversion — silent logic inversion if missed.** |
| Date/Time | 7, 133, 135 | `TEXT` | SQLite has no native date type. Dates are stored as ISO-8601 UTC strings (`YYYY-MM-DD HH:MM:SS`). |
| Text, Memo | 130, 202, 203 | `TEXT` | Length validation is deferred to the Domain layer. Case sensitivity will be handled using `COLLATE NOCASE` for lookups where appropriate. |
| Currency | 6 | `INTEGER` | Converted to minor units (cents) by multiplying by 100. EF Core SQLite cannot order/compare decimals reliably, so integer cents avoids float precision issues. |
| Double / Single | 4, 5 | `REAL` | |

## Parity Traps
- **Case sensitivity:** Access compares text case-insensitively; SQLite's `=` on `TEXT` is case-sensitive. Login and slug lookups must use `COLLATE NOCASE` or normalized columns.
- **Empty string vs NULL:** Access treats them differently but often UI obscures this. We maintain the source distinction.
- **Foreign Keys:** Relationships are not currently explicitly extracted by the simplistic VBScript exporter; foreign keys will be implicitly managed by the application logic during this phase, or explicit PRAGMA constraints can be added later if needed.
