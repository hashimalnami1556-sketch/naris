# NARSIC production dashboard

Generate the loading-style repository monitor:

```powershell
python tools/dashboard/render_progress_dashboard.py
```

Output:

`generated_designs/production_dashboard/NARSIC_PROGRESS_REPORT.html`

The canonical status input is `data/PRODUCTION_PROGRESS.json`.

The final desktop/dashboard visual must use English-only copy and must keep planning progress separate from runtime/QA evidence.
