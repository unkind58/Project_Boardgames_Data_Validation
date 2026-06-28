import os
from datetime import date, datetime, timedelta
from data_quality.gx.plugins.utils import record_start_time, calculate_execution_time, today

os.chdir("../")

start_time = record_start_time()
today = date.today()
start = str(today-timedelta(days=5))[:10]
today = str(today)[:10]
limit = None


PARAMS = [
    {"DQ_MODE": "incremental", "DQ_LAYER": "bronze", "DQ_DATASOURCE": "customers", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "bronze", "DQ_DATASOURCE": "employees", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "bronze", "DQ_DATASOURCE": "games_bgg", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "bronze", "DQ_DATASOURCE": "sales", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "silver", "DQ_DATASOURCE": "sales_enriched", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "gold", "DQ_DATASOURCE": "monthly_sales", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "gold", "DQ_DATASOURCE": "top_10_games", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "gold", "DQ_DATASOURCE": "employee_perform", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "gold", "DQ_DATASOURCE": "country_sales", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "reference", "DQ_DATASOURCE": "geography", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "reference", "DQ_DATASOURCE": "vendors", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "reference", "DQ_DATASOURCE": "delivery", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "reference", "DQ_DATASOURCE": "ga", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},
    {"DQ_MODE": "incremental", "DQ_LAYER": "reference", "DQ_DATASOURCE": "calendar", "DQ_FROM_DATE": start, "DQ_TO_DATE": today, "DQ_LIMIT": limit},

]

for values in PARAMS:
    try:
        os.environ["DQ_MODE"] = values["DQ_MODE"]
        os.environ["DQ_LAYER"] = values["DQ_LAYER"]
        os.environ["DQ_DATASOURCE"] = values["DQ_DATASOURCE"]
        if values.get("DQ_FROM_DATE", None):
            os.environ["DQ_FROM_DATE"] = values.get("DQ_FROM_DATE", None)
        if values.get("DQ_TO_DATE", None):
            os.environ["DQ_TO_DATE"] = values.get("DQ_TO_DATE", None)
        if values.get("DQ_LIMIT", None):
            os.environ["DQ_LIMIT"] = values.get("DQ_LIMIT", None)

        print('%run. / data_quality_gx.ipynb')

    except Exception as e:
        print(str(e))
    finally:
        keys_to_remove = ["DQ_MODE", "DQ_LAYER", "DQ_DATASOURCE", "DQ_FROM_DATE", "DQ_TO_DATE", "DQ_LIMIT"]
        for key in keys_to_remove:
            if key in os.environ:
                del os.environ[key]

calculate_execution_time(start_time)


