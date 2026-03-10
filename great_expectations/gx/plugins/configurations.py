import os
from datetime import datetime

from pyparsing import withClass
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round, filter
from delta import configure_spark_with_delta_pip
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

from great_expectations.gx.plugins.metadata import METADATA, REPORT_SCHEMA


class ConfigurationBase:
    def __init__(self):

        # Environment variables
        self.mode = self.get_env_var_lower('DQ_MODE')
        self.datasource = os.environ.get('DQ_DATASOURCE')
        self.layer = os.environ.get('DQ_LAYER')
        self.limit = os.environ.get('DQ_LIMIT', '0')
        self.from_date = os.environ.get('DQ_FROM_DATE','1900-01-01')
        self.to_date = os.environ.get('DQ_TO_DATE','2049-01-01')
        self.version = os.environ.get('DQ_VERSION', '0.1')

        # Other variables
        self.spark = None
        self.dq_report = None
        self.connection_time_out = '6000'
        self.datasource_map = METADATA
        self.path_prefix = self.get_path_prefix()
        self.data_format = self.get_data_format()
        self.result_path = 'validation_results/'
        self.result_format = 'delta'


    def get_env_var_lower(self,env_var_name):
        env_value = os.environ.get(env_var_name)
        return env_value.lower() if env_value else None


    def get_path_prefix(self):
        if self.layer and self.datasource:
            return self.datasource_map[self.layer][self.datasource]['path_prefix']
        else:
            return None


    def get_data_format(self):
        if self.layer and self.datasource:
            return self.datasource_map[self.layer][self.datasource]['format']
        else:
            return None


    def result_location(self):
        return f"{self.result_path}"


    def crate_spark_session(self, app_name='BGG Data Validation'):
        spark_builder = (
            SparkSession.builder.appName(app_name)
            .master("local[*]")
            .config("spark.driver.memory","16g")
            .config("spar.sql.debug.maxToStringFields","200")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.delta.logStore.class", "org.apache.spark.sql.delta.storage.LocalLogStore")
        )
        self.spark = configure_spark_with_delta_pip(spark_builder).getOrCreate()


    def generate_report(self, checkpoint_results, mode:str):
        table_data = []
        for result_key, result_value in checkpoint_results["run_results"].items():
            for result in result_value["validation_result"]["results"]:
                success = result["success"]
                unexpected_count = result["result"].get("unexpected_count", 0)
                unexpected_percent = result["result"].get("unexpected_percent")
                if unexpected_percent is not None:
                    percent = (100 - float(result["result"]["unexpected_percent"]))
                elif not result["success"]:
                    percent = 0
                else:
                    if isinstance(result["result"].get("partial_unexpected_counts"), list):
                        if len(result["result"].get("partial_unexpected_counts")) == 0 and unexpected_count is None:
                            percent = 0
                            success = 'false'
                    else:
                        percent = 100
                dimension = result["expectation_config"]["meta"]["dimension"]
                check_name = result["expectation_config"]["expectation_type"]
                column_name = result["expectation_config"]["kwargs"]["column"]\
                    if result["expectation_config"]["kwargs"].get("column")\
                    else str(result["expectation_config"]["kwargs"].get('column_list'))
                column_type = result["expectation_config"]["kwargs"].get("_type")
                element_count = result["result"].get("element_count", 0)
                unexpected_percent = result["result"].get("unexpected_percent", 0.0)
                partial_unexpected_list = result["result"].get("partial_unexpected_list")
                observed_value = result["result"].get("observed_value")
                exception_message = result["exception_info"].get("exception_message")\
                    if result.get('exception_info') else None

                table_data.append({
                    "RunName": f"{checkpoint_result.run_id.run_name}_{mode}",
                    "RunTime": checkpoint_result.run_id.run_time,
                    "DqMetric": dimension,
                    "SuccessPercentage": percent,
                    "CheckName": check_name,
                    "ColumnName": column_name,
                    "ColumnType": column_type,
                    "UnexpectedCount": unexpected_count,
                    "Success": success,
                    "Layer": self.layer,
                    "ElementCount": element_count,
                    "UnexpectedPercent": unexpected_percent,
                    "PartialUnexpectedValues": str(partial_unexpected_list if partial_unexpected_list else None),
                    "ObservedValue": observed_value,
                    "ExceptionMessage": exception_message,
                    "Year": checkpoint_result.run_id.run_time.year,
                    "Month": checkpoint_result.run_id.run_time.month,
                    "Day": checkpoint_result.run_id.run_time.day,
                    "Mode": self.mode,
                    "Entity": self.datasource,
                    "Limit": self.limit,
                    "FromDate": datetime.strptime(self.from_date, '%Y-%m-%d'),
                    "ToDate": datetime.strptime(self.to_date, '%Y-%m-%d')
                })

            self.dq_report = self.spark.createDataFrame(table_data, schema=REPORT_SCHEMA)


    def show_report(self, layer: str, datasource: str, summary_report: bool = True, detailed_report: bool = True):
        if summary_report:
            result_summary = self.dq_report.select("DqMetric", "SuccessPercentage")\
                .groupBy("DqMetric")\
                .agg(round(avg("SuccessPercentage"),2).alias("AverageSuccessPercentage"))

            print(f" {layer.title()}.{datasource.title()}")

            result_summary.select("DqMetric", "SuccessPercentage").orderBy("DqMetric").show(10)
        if detailed_report:
            result_summary = self.dq_report.select("DqMetric", "CheckName",
                                                   "ColumnName", "SuccessPercentage",
                                                   "UnexpectedCount", "Layer")\
            .withColumn("SuccessPercentage", round("SuccessPercentage", 2))\
            .filter((self.dq_report.Layer == layer)).orderBy("DqMetric", "CheckName", "ColumnName")

            print(f" {layer.title()}.{datasource.title()}")

            result_summary.show(100, truncate=False)



    def save_report(self):
        self.dq_report.write.format(self.result_format).mode("append").save(self.result_location())

