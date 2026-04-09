import logging
from datetime import datetime
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    LongType,
    StringType,
    DoubleType,
    TimestampType,
    DateType
)


from data_quality.gx.plugins.configurations import ConfigurationBase

class SparkConnector(ConfigurationBase):
    def __init__(self):
        super().__init__()

        self.logger: logging.Logger = logging.getLogger(SparkConnector.__name__)


    @property
    def path(self):
        return f"{self.path_prefix}"


    def connect(self):
        self.crate_spark_session()
        self.logger.info("SparkSession created successfully.")


    def read(self):
        if self.data_format == 'csv':
            self.logger.info(f"Data read successfully from {self.path} with format 'csv'.")
            return self.spark.read.format("csv").load(self.path, inferSchema=True, header=True)
        else:
            self.logger.info(f"Data read successfully from {self.path} with format {self.data_format}.")
            return self.spark.read.format(self.data_format).load(self.path)


    def read_data(self):
        try:
            df = self.read()
            self.logger.info(f'The "{self.datasource}" dataset is fetched in {self.mode} mode from {self.path} successfully.')
            if self.mode == 'full':
                return self.perform_filtering(df)
            elif self.mode == 'incremental':
                return self.perform_filtering(self.entity_incremental_query_factor(df))
            else:
                self.logger.warning(f'Unsupported mode "{self.mode}" for datasource "{self.datasource}".')
                return None
        except OSError as err:
            self.logger.info(f"Failed to read {self.datasource} data from {self.path} : {str(err)}")
            return None

    def perform_filtering(self, df):
        if self.datasource_map[self.layer][self.datasource].get('conditions'):
            df = df.where(f"{self.datasource_map[self.layer][self.datasource]['conditions']}")
        return df


    def entity_incremental_query_factor(self, df):
        incr_field = self.datasource_map[self.layer][self.datasource]['incr_field']
        if incr_field:
            if self.from_date not in ['', None, 'None']:
                df = df.filter(df[incr_field] >= self.from_date[:10])
            if self.to_date not in ['', None, 'None']:
                df = df.filter(df[incr_field] <= self.to_date[:10])
            if self.limit not in ['', None, 'None', '0']:
                df = df.limit(int(self.limit))
            self.logger.info("The dataset was filtered based on selected widget's parameters.")
        return df













