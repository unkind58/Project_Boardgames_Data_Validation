from pyspark.sql.types import (
    StructField,
    StringType,
    StructType,
    TimestampType,
    DoubleType,
    IntegerType,
    BooleanType,
    LongType
)


METADATA = {
    "bronze":{
        "customers":{
            "incr_field":'ingestion_timestamp',
            "path_prefix": 'data/bronze/customers/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
               "customer_id":{"data_type":"IntegerType", "nullable":False},
               "first_name":{"data_type":"StringType", "nullable":False},
               "last_name":{"data_type":"StringType", "nullable":False},
               "email":{"data_type":"StringType", "nullable":False},
               "country_id":{"data_type":"IntegerType", "nullable":False},
               "registration_date":{"data_type":"DateType", "nullable":False},
               "ingestion_timestamp":{"data_type":"TimestampType", "nullable":False},
               "source_system":{"data_type":"StringType", "nullable":False}
           }
        },
        "employees":{
            "incr_field":'ingestion_timestamp',
            "path_prefix": 'data/bronze/employees/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
                "employee_id":{"data_type":"StringType", "nullable":False},
                "first_name":{"data_type":"StringType", "nullable":False},
                "last_name":{"data_type":"StringType", "nullable":False},
                "email":{"data_type":"StringType", "nullable":False},
                "phone":{"data_type":"StringType", "nullable":True},
                "hire_date":{"data_type":"DateType", "nullable":True},
                "birth_date":{"data_type":"DateType", "nullable":True},
                "country_id":{"data_type":"IntegerType", "nullable":False},
                "ingestion_timestamp":{"data_type":"TimestampType", "nullable":False},
                "source_system":{"data_type":"StringType", "nullable":False}
            }
        },
        "games_bgg":{
            "incr_field":'ingestion_timestamp',
             "path_prefix": 'data/bronze/bgg_games/',
             "format":'delta',
             "run_mode":['full','incremental'],
             "model": {
                 "rank":{"data_type":"IntegerType", "nullable":True},
                 "bgg_url":{"data_type":"StringType", "nullable":False},
                 "game_id":{"data_type":"IntegerType", "nullable":False},
                 "names":{"data_type":"StringType", "nullable":False},
                 "min_players":{"data_type":"IntegerType", "nullable":True},
                 "max_players":{"data_type":"IntegerType", "nullable":True},
                 "avg_time":{"data_type":"IntegerType", "nullable":True},
                 "min_time":{"data_type":"IntegerType", "nullable":True},
                 "max_time":{"data_type":"IntegerType", "nullable":True},
                 "year":{"data_type":"IntegerType", "nullable":True},
                 "avg_rating":{"data_type":"DoubleType", "nullable":True},
                 "geek_rating":{"data_type":"DoubleType", "nullable":True},
                 "num_votes":{"data_type":"IntegerType", "nullable":True},
                 "image_url":{"data_type":"StringType", "nullable":True},
                 "age":{"data_type":"IntegerType", "nullable":True},
                 "mechanic":{"data_type":"StringType", "nullable":True},
                 "owned":{"data_type":"IntegerType", "nullable":True},
                 "category":{"data_type":"StringType", "nullable":True},
                 "designer":{"data_type":"StringType", "nullable":True},
                 "weight":{"data_type":"DoubleType", "nullable":True},
                 "ingestion_timestamp":{"data_type":"TimestampType", "nullable":False},
                 "source_system":{"data_type":"StringType", "nullable":False}
             }
        },
        "sales":{
            "incr_field":'ingestion_timestamp',
            "path_prefix": 'data/bronze/sales/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model": {
                 "sale_id":{"data_type":"LongType", "nullable":False},
                 "sale_timestamp":{"data_type":"TimestampType", "nullable":False},
                 "customer_id":{"data_type":"IntegerType", "nullable":False},
                 "game_id":{"data_type":"IntegerType", "nullable":False},
                 "quantity":{"data_type":"IntegerType", "nullable":False},
                 "unit_cost":{"data_type":"DoubleType", "nullable":False},
                 "unit_price":{"data_type":"DoubleType", "nullable":False},
                 "currency_code":{"data_type":"StringType", "nullable":False},
                 "payment_method_code":{"data_type":"StringType", "nullable":False},
                 "delivery_id":{"data_type":"StringType", "nullable":False},
                 "employee_id":{"data_type":"StringType", "nullable":False},
                 "vendor_id":{"data_type":"StringType", "nullable":False},
                 "ga_id":{"data_type":"StringType", "nullable":False},
                 "ingestion_timestamp":{"data_type":"TimestampType", "nullable":False},
                 "source_system":{"data_type":"StringType", "nullable":False}
            }
        }
    },
     "silver":{
        "sales_enriched":{
            "incr_field":'silver_processed_timestamp',
            "path_prefix": 'data/silver/sales_enriched/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
                "date":{"data_type":"DateType", "nullable":False},
                "ga_id":{"data_type":"StringType", "nullable":False},
                "delivery_id":{"data_type":"StringType", "nullable":False},
                "vendor_id":{"data_type":"StringType", "nullable":False},
                "game_id":{"data_type":"IntegerType", "nullable":False},
                "employee_id":{"data_type":"StringType", "nullable":False},
                "customer_id":{"data_type":"IntegerType", "nullable":False},
                "sale_id":{"data_type":"LongType", "nullable":False},
                "sale_timestamp":{"data_type":"TimestampType", "nullable":False},
                "quantity":{"data_type":"IntegerType", "nullable":False},
                "unit_cost":{"data_type":"DoubleType", "nullable":False},
                "unit_price":{"data_type":"DoubleType", "nullable":False},
                "currency_code": {"data_type": "StringType", "nullable": False},
                "payment_method_code":{"data_type":"StringType", "nullable":False},
                "customer_first_name":{"data_type":"StringType", "nullable":False},
                "customer_last_name":{"data_type":"StringType", "nullable":False},
                "customer_country_id":{"data_type":"IntegerType", "nullable":False},
                "registration_date":{"data_type":"DateType", "nullable":False},
                "employee_first_name":{"data_type":"StringType", "nullable":False},
                "employee_last_name":{"data_type":"StringType", "nullable":False},
                "employee_country_id":{"data_type":"IntegerType", "nullable":False},
                "hire_date":{"data_type":"DateType", "nullable":True},
                "game_name":{"data_type":"StringType", "nullable":False},
                "avg_rating":{"data_type":"DoubleType", "nullable":True},
                "category":{"data_type":"StringType", "nullable":True},
                "mechanic":{"data_type":"StringType", "nullable":True},
                "vendor_name":{"data_type":"StringType", "nullable":False},
                "vendor_country":{"data_type":"StringType", "nullable":False},
                "delivery_company_name":{"data_type":"StringType", "nullable":False},
                "ga_device_type":{"data_type":"StringType", "nullable":False},
                "ga_source_id":{"data_type":"StringType", "nullable":False},
                "year":{"data_type":"IntegerType", "nullable":False},
                "month":{"data_type":"IntegerType", "nullable":False},
                "month_name":{"data_type":"StringType", "nullable":False},
                "day":{"data_type":"IntegerType", "nullable":False},
                "day_of_week":{"data_type":"IntegerType", "nullable":False},
                "week_of_year":{"data_type":"IntegerType", "nullable":False},
                "quarter":{"data_type":"IntegerType", "nullable":False},
                "is_weekend":{"data_type":"BooleanType", "nullable":False},
                "is_month_start":{"data_type":"BooleanType", "nullable":False},
                "is_month_end":{"data_type":"BooleanType", "nullable":False},
                "customer_country_name":{"data_type":"StringType", "nullable":False},
                "customer_region_name":{"data_type":"StringType", "nullable":False},
                "customer_continent_name":{"data_type":"StringType", "nullable":False},
                "employee_country_name":{"data_type":"StringType", "nullable":False},
                "employee_region_name":{"data_type":"StringType", "nullable":False},
                "employee_continent_name":{"data_type":"StringType", "nullable":False},
                "total_revenue":{"data_type":"DoubleType", "nullable":False},
                "total_cost":{"data_type":"DoubleType", "nullable":False},
                "total_profit":{"data_type":"DoubleType", "nullable":False},
                "profit_margin_pct":{"data_type":"DoubleType", "nullable":False},
                "is_new_customer":{"data_type":"BooleanType", "nullable":False},
                "silver_processed_timestamp":{"data_type":"TimestampType", "nullable":False}
            }
        },
    },
    "gold": {
        "country_sales":{
            "incr_field":'gold_generated_timestamp',
            "path_prefix": 'data/gold/country_sales/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
                "customer_country_name":{"data_type":"StringType", "nullable":False},
                "total_revenue":{"data_type":"DoubleType", "nullable":False},
                "avg_profit_margin_pct":{"data_type":"DoubleType", "nullable":False},
                "gold_generated_timestamp":{"data_type":"TimestampType", "nullable":False}
            }
        },
        "monthly_sales":{
            "incr_field":'gold_generated_timestamp',
            "path_prefix": 'data/gold/monthly_sales_summary/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
                "year":{"data_type":"IntegerType", "nullable":False},
                "month":{"data_type":"IntegerType", "nullable":False},
                "total_revenue":{"data_type":"DoubleType", "nullable":False},
                "total_profit":{"data_type":"DoubleType", "nullable":False},
                "total_orders":{"data_type":"IntegerType", "nullable":False},
                "gold_generated_timestamp":{"data_type":"TimestampType", "nullable":False}
            }
        },
        "top_10_games":{
            "incr_field":'gold_generated_timestamp',
            "path_prefix": 'data/gold/top_10_games/',
            "format":'delta',
            "run_mode":['full','incremental'],
            "model":{
                "year": {"data_type": "IntegerType", "nullable": False},
                "month": {"data_type": "IntegerType", "nullable": False},
                "game_name": {"data_type": "StringType", "nullable": False},
                "montly_total_revenue": {"data_type": "DoubleType", "nullable": False},
                "rank": {"data_type": "IntegerType", "nullable": False},
                "gold_generated_timestamp": {"data_type": "TimestampType", "nullable": False}
            }
        },
        "employee_perform":{
            "incr_field": 'gold_generated_timestamp',
            "path_prefix": 'data/gold/employee_performance/',
            "format": 'delta',
            "run_mode": ['full', 'incremental'],
            "model":{
                "year": {"data_type": "IntegerType", "nullable": False},
                "month": {"data_type": "IntegerType", "nullable": False},
                "employee_name": {"data_type": "StringType", "nullable": False},
                "total_sales": {"data_type": "DoubleType", "nullable": False},
                "total_profit": {"data_type": "DoubleType", "nullable": False},
                "gold_generated_timestamp": {"data_type": "TimestampType", "nullable": False}
            }
        }
    },
    "reference":{
        "geography":{
            "incr_field":None,
            "path_prefix": 'data/reference/geography/',
            "format":'delta',
            "run_mode": ['full'],
            "model":{
                "country_id":{"data_type":"IntegerType", "nullable":False},
                "country_name":{"data_type":"StringType", "nullable":False},
                "country_code":{"data_type":"StringType", "nullable":False},
                "region_id": {"data_type": "IntegerType", "nullable": False},
                "region_name":{"data_type":"StringType", "nullable":False},
                "continent_id":{"data_type":"IntegerType", "nullable":False},
                "continent_name":{"data_type":"StringType", "nullable":False}
            }
        },
        "vendors":{
            "incr_field":None,
            "path_prefix": 'data/reference/vendors/',
            "format":'delta',
            "run_mode": ['full'],
            "model":{
                "vendor_id":{"data_type":"StringType", "nullable":False},
                "vendor_name":{"data_type":"StringType", "nullable":False},
                "vendor_country":{"data_type":"StringType", "nullable":False},
                "vendor_city":{"data_type":"StringType", "nullable":True},
                "vat_number":{"data_type":"StringType", "nullable":True}
            }
        },
        "delivery":{
            "incr_field":None,
            "path_prefix": 'data/reference/delivery/',
            "format":'delta',
            "run_mode": ['full'],
            "model":{
                "delivery_id":{"data_type":"StringType", "nullable":False},
                "delivery_company_name":{"data_type":"StringType", "nullable":False},
                "delivery_type":{"data_type":"StringType", "nullable":False}
            }
        },
        "ga":{
            "incr_field":None,
            "path_prefix": 'data/reference/google_analytics/',
            "format":'delta',
            "run_mode": ['full'],
            "model":{
                "ga_id":{"data_type":"StringType", "nullable":False},
                "ga_source_id":{"data_type":"StringType", "nullable":False},
                "ga_device_type":{"data_type":"StringType", "nullable":False}
            }
        },
        "calendar": {
            "incr_field": None,
            "path_prefix": 'data/reference/calendar/',
            "format": 'delta',
            "run_mode": ['full'],
            "model": {
                "date": {"data_type": "DateType", "nullable": False},
                "year": {"data_type": "IntegerType", "nullable": False},
                "month": {"data_type": "IntegerType", "nullable": False},
                "month_name": {"data_type": "StringType", "nullable": False},
                "day": {"data_type": "IntegerType", "nullable": False},
                "day_of_week": {"data_type": "IntegerType", "nullable": False},
                "week_of_year": {"data_type": "IntegerType", "nullable": False},
                "quarter": {"data_type": "IntegerType", "nullable": False},
                "is_weekend": {"data_type": "BooleanType", "nullable": False},
                "is_month_start": {"data_type": "BooleanType", "nullable": False},
                "is_month_end": {"data_type": "BooleanType", "nullable": False}
            }
        }
    }
}

REPORT_SCHEMA = StructType([
    StructField("RunName", StringType(), True),
    StructField("RunTime", TimestampType(), True),
    StructField("DqMetric", StringType(), True),
    StructField("CheckName", StringType(), True),
    StructField("ColumnName", StringType(), True),
    StructField("Success", StringType(), True),
    StructField("SuccessPercentage", StringType(), True),
    StructField("UnexpectedCount", IntegerType(), True),
    StructField("Layer", StringType(), True),
    StructField("ColumnType", StringType(), True),
    StructField("ElementCount", IntegerType(), True),
    StructField("UnexpectedPercent", DoubleType(), True),
    StructField("PartialUnexpectedValues", StringType(), True),
    StructField("ObservedValue", StringType(), True),
    StructField("ExceptionMessage", StringType(), True),
    StructField("Year", IntegerType(), True),
    StructField("Month", IntegerType(), True),
    StructField("Day", IntegerType(), True),
    StructField("Mode", StringType(), True),
    StructField("Entity", StringType(), True),
    StructField("Limit", StringType(), True),
    StructField("FromDate", TimestampType(), True),
    StructField("ToDate", TimestampType(), True)
])
