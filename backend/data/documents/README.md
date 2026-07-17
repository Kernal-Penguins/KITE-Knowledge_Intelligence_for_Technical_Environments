# KITE — Industrial Document Repository

This directory holds the real industrial documents that KITE ingests.

## ⚠️ Important: These files are NOT committed to git

Add your actual documents below. The ingestion pipeline auto-detects `doc_type` from the subdirectory name.

## File Naming Convention

```
{equipment_tag}_{doc_type}_{YYYYMMDD}.{ext}
```

Examples:
- `P104_maintenance_log_20260315.pdf`
- `V201_inspection_report_20260502.docx`
- `all_sops_pump_lockout_20250110.pdf`

## Supported Formats

| Format | Extension |
|--------|-----------|
| PDF    | `.pdf`    |
| Word   | `.docx`   |
| CSV    | `.csv`    |
| Image (P&ID stretch goal) | `.png`, `.jpg`, `.pdf` |

## Directory Structure

```
documents/
├── maintenance_logs/      ← Add maintenance log PDF/DOCX here
├── sops/                  ← Add SOP PDF/DOCX here
├── inspection_reports/    ← Add inspection report PDF/DOCX here
├── work_orders/           ← Add work order PDF/DOCX/CSV here
├── incidents/             ← Add incident/near-miss PDF/DOCX here
└── pid_samples/           ← Add P&ID image files here (stretch goal)
```

## Tips

- Equipment IDs should recur **across** document types — this is what creates graph structure.
- Include at least one equipment ID in multiple documents (e.g. `P-104` appears in a maintenance log, a work order, and an inspection report).
- The entity resolution pass will merge references like `"P-104"`, `"Pump 104"`, and `"P104"` into a single canonical node.
