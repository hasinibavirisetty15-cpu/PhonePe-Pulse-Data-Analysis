# How to run (Windows)

Open **Command Prompt** (or the VS Code terminal) in the project folder, then:

```
:: one-time setup
python -m pip install -r requirements.txt
mkdir data\raw
:: copy the 6 ORIGINAL csv files into data\raw
::   aggregated_transaction.csv  aggregated_user.csv  map_transaction.csv
::   map_user.csv  top_transaction.csv  top_user.csv

:: run in this order
python scripts\build_master_table.py     :: merges the 6 files -> data\master_long.csv + data\master_district_quarter.csv
python scripts\validate_data.py          :: -> reports\validation_report.md
python scripts\compute_kpis.py           :: -> outputs\*.csv (YoY, CAGR, KPIs, top lists, recommendation table)
streamlit run app\streamlit_app.py       :: opens the dashboard in your browser
```

If `python` is not found, try `py` instead of `python`.
Your existing files (README.md, dashboard.png, pp_dashboard.csv, prepare_data.py) are not touched by any of these scripts.
