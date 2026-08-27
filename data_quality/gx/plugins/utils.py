import os
import textwrap
import ipywidgets as widgets
from marshmallow import missing
from pyspark.sql import DataFrame, SparkSession
from datetime import date, timedelta, datetime
from data_quality.gx.plugins.metadata import METADATA
from data_quality.gx.plugins.connectors import SparkConnector


import seaborn as sns
import matplotlib.pyplot as plt

from pyspark.sql.window import Window
from pyspark.sql.functions import (
    count, date_sub, col, round, lit, when,
    avg, max as spark_max, date_format, concat,desc,
    row_number, dense_rank, countDistinct
)

today = date.today()
start = today - timedelta(days=5)

def record_start_time():
    return datetime.now()

def extract_param_values():
    values_dict = {key_a: list(value_a.keys()) for key_a, value_a in METADATA.items()}
    run_mode_dict = {key_b: value_b['run_mode'] for value_a in METADATA.values() for key_b, value_b in value_a.items()}
    return values_dict, run_mode_dict

def calculate_execution_time(start_time):
    end_time = datetime.now()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time.total_seconds()} seconds")

ds_layer, run_mode = extract_param_values()

def initialize_widgets():
    params_to_disable = {'full': True, 'incremental': False}

    def print_params(layer, ds, mode, from_date='', to_date='', limit=''):
        os.environ["DQ_MODE"] = mode
        os.environ["DQ_LAYER"] = layer
        os.environ["DQ_DATASOURCE"] = ds
        os.environ["DQ_FROM_DATE"] = str(from_date)[:10]
        os.environ["DQ_TO_DATE"] = str(to_date)[:10]
        os.environ["DQ_LIMIT"] = str(limit)
        from_date_w.disabled = params_to_disable[os.environ["DQ_MODE"]]
        to_date_w.disabled = params_to_disable[os.environ["DQ_MODE"]]
        limit_w.disabled = params_to_disable[os.environ["DQ_MODE"]]

    def select_layer(layer):
        layer_w.options = ds_layer[layer]

    def select_mode(ds):
        mode_w.options = run_mode[ds]

    sc_w = widgets.Dropdown(options=ds_layer.keys(),
                            value = os.environ.get('DQ_LAYER', 'bronze'),
                            description='Layer:',
                            disabled=False)

    layer_w = widgets.Dropdown(options=ds_layer[sc_w.value],
                               value = os.environ.get('DQ_DATASOURCE', 'customers'),
                               row=3,
                               description='Datasource:',
                               disabled=False)

    mode_w = widgets.Dropdown(options=run_mode[layer_w.value],
                              value = os.environ.get('DQ_MODE', 'incremental'),
                              description='Run Mode:',
                              disabled=False)

    from_date_w = widgets.DatePicker(
        value=datetime.strptime(os.environ.get('DQ_FROM_DATE', str(start))[:10], '%Y-%m-%d'),
        description='From Date:',
        disabled=params_to_disable[mode_w.value]
    )

    to_date_w = widgets.DatePicker(
        value=datetime.strptime(os.environ.get('DQ_TO_DATE', str(today))[:10], '%Y-%m-%d'),
        description='To Date:',
        disabled=params_to_disable[mode_w.value]
    )

    limit_w = widgets.Text(
        value=os.environ.get('DQ_LIMIT', '1000000'),
        placeholder='1000000',
        description='Record Limit:',
        disabled=params_to_disable[mode_w.value]
    )

    widgets_combined = widgets.interactive(print_params, layer=sc_w, ds=layer_w, mode=mode_w, from_date=from_date_w,
                                           to_date=to_date_w, limit=limit_w)
    widgets_layer = widgets.interactive(select_layer, layer=sc_w)
    widgets_mode = widgets.interactive(select_mode, ds=layer_w)

    return widgets_combined


#################################
####### Test Resul Report #######
#################################


def load_test_result_report(spark_connector: SparkConnector, result_location: str) -> DataFrame :
    df = spark_connector.spark.read.format("delta").load(result_location)

    return df


def filter_dataframe_back_days(df: DataFrame, days_back: int) -> DataFrame:
    current_day = date.today()
    start_date = current_day - timedelta(days=days_back)
    start_timestamp = datetime.combine(start_date, datetime.min.time())

    return df.filter(col('Runtime') >= lit(start_timestamp))


def apply_two_windows_functions(df: DataFrame) -> DataFrame:
    """
    - Apply two window functions to the DataFrame: row_number() and max()
    """

    window_spec1 = Window.partitionBy("DqMetric", "CheckName", "Layer", "Entity", "ColumnName").orderBy(desc("Runtime"))
    window_spec2 = Window.partitionBy("Layer", "Entity").orderBy(desc("Runtime"))


    return df.withColumn("RowNum", dense_rank().over(window_spec1)) \
                .withColumn("max_Runtime", spark_max(col("Runtime")).over(window_spec2))


def filter_run_over_run(df:DataFrame) -> DataFrame:
    """
    Filters the DataFrame to keep only the first two row numbers taken by latest two runs filtered by RunTime
    """

    window = Window.partitionBy("Layer", "Entity", "RowNum").orderBy(desc("Runtime"))
    df = df.withColumn("max_RunTime_by_RowNum", spark_max(col("Runtime")).over(window))

    return df.filter(((col("RowNum") == 1) | (col("RowNum") == 2)) & (col("Runtime") == col("max_RunTime_by_RowNum")))


def filter_last_run(df: DataFrame) -> DataFrame:
    """
    (1) Extracts the last run by filtering the first row.
    (2) Drops unnecessary columns: RowNum, max_Runtime.
    (3)  Filters are based on th maximum runtime to include only the last run.
    """

    return df.filter(col("RowNum") == 1).filter(col("Runtime") == col("max_Runtime")).drop("RowNum", "max_Runtime")


def filter_failed_critical_checks(df: DataFrame, critical_checks: list) -> DataFrame:
    """
    Filters the DataFrame to keep only the failed critical checks.
    """

    df = df.filter(col('CheckName').isin(critical_checks)).filter("Success = false").toPandas()
    df["SuccessPercentage"] = df["SuccessPercentage"].astype(float).apply(lambda x: f"{x:.2f}")

    return df


def filter_for_main_charts(df: DataFrame) -> DataFrame:
    """
    Filters the DataFrame to keep only entities defined in METADATA.
    """
    values_dict = {key: list(value.keys()) for key, value in METADATA.items()}
    metadata_entities = set().union(* values_dict.values())

    return df.filter(col('Entity').isin(metadata_entities))


def filter_for_run_over_run_bar_charts(df: DataFrame) -> DataFrame:
    """
    Filters the DataFrame to keep only the last two runs for each layer and entity,
    and calculates the average success percentage for each layer and entity by Data Quality dimension.
    """
    df_5days_range_avg_count_per_layer_and_entity_by_dimension = df.groupBy("Layer", "DqMetric" , "Entity", "RowNum") \
        .agg(round(avg(col("SuccessPercentage")), 2).alias("checks_success_percentage_by_layer_and_entity_by_dimension"))
    df_range_run_over_run = df_5days_range_avg_count_per_layer_and_entity_by_dimension.toPandas()

    mapping = {1: "Current Run", 2: "Previous Run"}
    df_range_run_over_run["RowNum"] = df_range_run_over_run["RowNum"].map(mapping)

    return df_range_run_over_run


def apply_filters_and_get_multiple_dataframes(tr_df, spark_connector: SparkSession, days_back: int):
    """
    Applies a series of filters to the input DataFrame and returns multiple filtered DataFrames.

    :param tr_df: Input Test Results DataFrame to be filtered.
    :param spark_connector: SparkSession object for Spark operations.
    :param days_back: Number of days to look back for filtering the DataFrame.

    :return: A tuple containing the following filtered DataFrames:
        - df_back_days_range_run_over_run: Filtered DataFrame for a specific range days used for run-over-run chart.
        - df_latest_run: Filtered DataFrame containing only the latest run based on the maximum runtime.
        - df: Filtered DataFrame containing only valid and expected entities defined in METADATA for main charts.
        - df_range_run_over_run: Filtered DataFrame for run-over-run bar charts with average success percentage.

    """

    # [Step 1] Filtering the DataFrame for the last 'days_back' days
    tr_df = filter_dataframe_back_days(tr_df, days_back)

    # [Step 2] Applying two window functions to the DataFrame
    tr_df = apply_two_windows_functions(tr_df)

    # [Step 3] Creating separate DataFrame with current and previous runs
    df_back_days_range_run_over_run = filter_run_over_run(tr_df)

    # [Step 4] Creating a separate DataFrame with the last run: checking the maximum runtime to include only the last run
    df_latest_run = filter_last_run(tr_df)

    # [Step 5] Creating a separate DataFrame with valid and expected list of entities defined in METADATA
    df = filter_for_main_charts(df_latest_run)

    # [Step 6] Creating and applying filters for the run-over-run bar charts
    df_range_run_over_run = filter_for_run_over_run_bar_charts(df_back_days_range_run_over_run)

    # [Step 7] Creating and applying filters for separate DataFrame with failed critical Data Quality checks
    df_critical_issues = filter_failed_critical_checks(df_latest_run, spark_connector.critical_checks)

    return df_back_days_range_run_over_run, df_latest_run, df, df_range_run_over_run, df_critical_issues


def set_pie_chart_variables(df: DataFrame, df_run_over_run: DataFrame, env: str = "TEST") -> dict:
    result_dict = {"environment": env, "total_check_count": df.count()}

    df_success_calc = df.groupBy("Success").agg({"Success": "count"}) \
        .withColumnRenamed("Success", "passed") \
        .withColumnRenamed("count(Success)", "success_count_per_run")

    df_success_rate = df_success_calc.select("*").toPandas()

    perc = ((df_success_rate[df_success_rate['passed'] == 'true']['success_count_per_run'].values[0]) / (
        df_success_rate['success_count_per_run'].sum())).round(4)
    result_dict["percentage"] = "{:.2%}".format(perc)

    max_time = df.agg({"Runtime": "max"}).collect()[0][0]
    min_time = df.agg({"Runtime": "min"}).collect()[0][0]
    count_for_run_time = df_run_over_run.groupBy("Layer", "Entity").agg(countDistinct("Day").alias("DistinctDays"))

    # Calculate delta days between max and min runtime, noting runtime is omitted if the two most recent runs share the same day.
    if count_for_run_time.select("DistinctDays").distinct().count() > 1:
        result_dict["runtime"] = 'not available'
    else:
        result_dict["runtime"] = max_time - min_time

    count_for_run_date = df.groupBy("Layer", "Entity").agg(countDistinct("Day").alias("DistinctDays"))

    if count_for_run_date.select("DistinctDays").distinct().count() > 1:
        result_dict["run_date"] = 'not available'
    else:
        result_dict["run_date"] = df.agg({"Runtime": "max"}).select(date_format(col("max(Runtime)"),
                                                                                "yyyy-MM-dd")).first()[0]

    return result_dict


def plot_success_percentage_pie_chart(df: DataFrame, variables: dict):
    df_success_calc = df.groupBy(df.Success).agg({"Success": "count"}) \
        .withColumnRenamed("Success", "passed") \
        .withColumnRenamed("count(Success)", "success_count_per_run")
    df_success_rate = df_success_calc.select("*").toPandas()

    plt.figure(figsize=(10, 6))

    pie = plt.pie(df_success_rate['success_count_per_run'],
                  shadow=True,
                  startangle=90,
                  labels=df_success_rate['success_count_per_run'],
                  colors=['red','green'],
                  labeldistance=0.66,
                  textprops={'fontsize': 15}
                  )

    plt.legend(labels=['Failed','Passed'], bbox_to_anchor=(0.6, -0.05),ncol=5)

    plt.axis('equal')

    plt.text(x=1.2,y=0.5, s=f"Total checks: {variables['total_check_count']}",
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'), fontsize=22)
    plt.text(x=1.2,y=0.2, s=f"Environment: {variables['environment']}",
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'), fontsize=22)
    plt.text(x=1.2,y=-0.1, s=f"Date of run: {variables['run_date']}",
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'), fontsize=22)
    plt.text(x=1.2,y=-0.4, s=f"Run Time: {variables['runtime']}",
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'), fontsize=22)
    plt.text(x=1.2,y=-0.7, s=f"PASS percentage: {variables['percentage']}",
             bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'), fontsize=22)

    plt.title(label=f"Data Quality Checks Success Rate", fontsize=15)

    plt.gca().get_xaxis().set_visible(False)
    plt.gca().get_yaxis().set_visible(False)
    plt.tight_layout()
    white_circle = plt.Circle((0, 0), 0.825, fc='white')
    plt.gca().add_artist(white_circle)
    plt.show(block=False)


def plot_success_percentage_bar_chart(df: DataFrame):
    alpha = 0.55
    custom_palette = {
        'bronze': '#CD7F32',
        'silver': '#A9A9A9',
        'gold': '#D4AF37',
        'reference': '#228B22'
    }

    df_per_layer_per_dq_metric = df.select(["CheckName", "SuccessPercentage", "Layer", "DqMetric", "Entity"])
    df_avg_count_per_layer_per_dq_metric = df_per_layer_per_dq_metric.groupBy("Layer", "DqMetric").agg(
        round(avg(col("SuccessPercentage")), 2).alias("Avg_SuccessPercentage"),
        count(col("SuccessPercentage")).alias("Count_SuccessPercentage"),
        count(when((col("SuccessPercentage") == 100), 1)).alias("Count_Passed_SuccessPercentage")) \
        .withColumn("Count_Passed_VS_Overall_SuccessPercentage",
                    concat(col("Count_Passed_SuccessPercentage"),
                           lit("/"), col("Count_SuccessPercentage")
                           )
    )

    df_metric = df_avg_count_per_layer_per_dq_metric.toPandas()
    df_metric = df_metric[["Layer", "DqMetric", "Avg_SuccessPercentage", "Count_SuccessPercentage"]].copy()
    pivoted_df = df_metric.pivot(index='Layer', columns='DqMetric', values='Avg_SuccessPercentage').reset_index()
    pivoted_df_success_rate = df_metric.pivot(index='Layer', columns='DqMetric', values='Count_SuccessPercentage').reset_index().fillna(0.0)
    passed_values = [
        pivoted_df_success_rate["Completeness"].tolist(),
        pivoted_df_success_rate["Integrity"].tolist(),
        pivoted_df_success_rate["Uniqueness"].tolist(),
        pivoted_df_success_rate["Validity"].tolist()
    ]

    fig, ax = plt.subplots(1, 4, figsize=(22,9), sharey=True)
    sns.barplot(x=pivoted_df.Layer, y=pivoted_df.Completeness, ax=ax[0], palette=custom_palette ,alpha=alpha)
    sns.barplot(x=pivoted_df.Layer, y=pivoted_df.Integrity, ax=ax[1], palette=custom_palette ,alpha=alpha)
    sns.barplot(x=pivoted_df.Layer, y=pivoted_df.Uniqueness, ax=ax[2], palette=custom_palette ,alpha=alpha)
    sns.barplot(x=pivoted_df.Layer, y=pivoted_df.Validity, ax=ax[3], palette=custom_palette ,alpha=alpha)

    plt.suptitle("Data Quality Success Percentage by Data Quality Dimension and Layer", fontsize=18, y=1)

    for i, patch in enumerate([ax[0].patches, ax[1].patches, ax[2].patches, ax[3].patches]):
        for p in patch:
            ax[i].annotate(
                "{:.2f}%".format(p.get_height()),
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center',
                va='center',
                bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'),
                xytext=(0, 8),
                textcoords='offset points',
            )
            ax[i].tick_params(axis='x', labelsize=7.5)
            ax[i].axhline(80, zorder=1, linewidth=0.1, color='tomato')
            for e, v in enumerate(passed_values[i]):
                ax[i].text(e, 5.0, int(v), ha='center', va='bottom', fontsize=8,
                           bbox=dict(facecolor='white', edgecolor='black', boxstyle='sawtooth'))
                ax[i].text(e, 1.8, 'checks', ha='center', va='bottom', fontsize=7,
                           bbox=dict(facecolor='white', edgecolor='black', boxstyle='sawtooth'))

    titles = ['Completeness', 'Integrity', 'Uniqueness', 'Validity']

    for i, title in enumerate(titles):
        ax[i].set(title=title)
        ax[i].set(xlabel='')
        ax[i].set(ylabel='')


def plot_success_percentage_heatmap(df: DataFrame):
    df_heatmap = df.select(["Layer", "DqMetric", "Entity", "Success", "SuccessPercentage"]) \
        .withColumn("Layer_Entity", concat(col("Layer"), lit("_"), col("Entity")))
    df_heatmap_avg = df_heatmap.groupBy("Layer_Entity", "DqMetric").agg(round(avg(col("SuccessPercentage")), 2).alias("Avg_SuccessPercentage"))
    pivoted_heatmap = df_heatmap_avg.toPandas().pivot(index='Layer_Entity', columns='DqMetric', values='Avg_SuccessPercentage').fillna(0.0)

    f, ax = plt.subplots(figsize=(17, 10))
    sns.heatmap(pivoted_heatmap,
                annot=True,
                robust=False,
                cmap='RdYlGn',
                ax=ax,
                fmt='g',
                vmin=0,
                vmax=100)
    plt.ylabel(None)
    plt.suptitle("Data Quality Success Percentage Heatmap by Data Quality Dimension per Layer and Entity",
                 fontsize=18, y=0.92,x=0.42)
    plt.show()

def plot_failed_dq_checks_table(df: DataFrame):
    def wrap_text(text, width=25):
        """
        Wraps the input text to a specified width for better readability for users.
        """
        return '\n'.join(textwrap.wrap(str(text), width=width))

    # Ensure the DataFrame contains all required columns before proceeding
    columns_for_table = ["Layer", "Entity", "DqMetric", "CheckName", "ColumnName", "SuccessPercentage", "UnexpectedCount"]
    try:
        df_dq_issues = df.select(columns_for_table).copy(deep=True)
    except KeyError as err:
        missing_cols = set(columns_for_table) - set(df.columns)
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}. Please ensure the DataFrame contains all required columns.") from err

    df_wrapped_text = df_dq_issues.applymap(lambda x: wrap_text(x, width=30)).sort_values(by="Layer").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_wrapped_text.values, colLabels=df_wrapped_text.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.5,5.5)


    # Apply Bold formatting to the header row
    for col in table.get_celld().keys():
        if col[0] == 0:  # Header row
            table.get_celld()[col].set_text_props(weight='bold')

    #Define colors for the rows based on the "Layer" column
    alpha = 0.15





