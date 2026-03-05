# Project_Boardgames_Data_Validation
This is BGG dataset, shortened to TOP-4999 games, enhanced with randomly generated data for data validation purposes

## Overview
This repository contains a dataset derived from BoardGameGeek (BGG) that has been enhanced with randomly generated data and Data Quality Framework (DQF) used to test this dataset.

The DQF is based on open-source tool 'Great Expectations' and provides the capability to ensure that data is loaded and processed correctly across various medallion layers.

It provides verification checks to validate data objects, aggregations, schemas, joins, data types, transformations and enrichment, while tracking key dataset characteristics over time, including row counts, null values, uniqueness, and referential integrity.

## Local Environment Setup
Below listed packages are required to set up the local environment.

- JupyterHub
- Poetry
- Python 3.11+
- Java JDK 11+ 
- Hadoop (winutils.exe & hadoop.dll, required on Windows for PySpark)

 After installing Python 3.11+, Java JDK 11+ (required for PySpark) and Hadoop, make sure to:
 - set the `JAVA_HOME` environment variable to point to your JDK folder
 - add `%JAVA_HOME%\bin` to your system PATH
 - set the `HADOOP_HOME` environment variable to point to bin directory
 - add `%HADOOP_HOME%\bin` to your system PATH
 - add Python folder containing `python.exe` to your system PATH 

## Installation of Dependencies and run JupyterHub
To install the required dependencies, please use `poetry``. 
Run the following command in your terminal:

```bash
    poetry install
   ```
Activate environment:

```bash
    poetry env activate
   ```
Register the kernel for JupyterHub:

```bash
    python -m ipykernel install --user --name=boardgames-env --display-name "Python 3.11 (boardgames-env)"
   ```
Run JupyterHub:

```bash
    jupyter notebook
   ```
Select the kernel `Python 3.11 (boardgames-env)` in your notebooks.

## Generate Data for Data Validation
In order to generate Data for Data Validation, run the following notebooks in the order listed below:
1. notebooks/`01_generate_and_enhance_reference_data.ipynb` - generates reference data for data validation.
2. notebooks/`02_generate_and_enhance_bronze_data.ipynb` - generates bronze data for data validation, which is the raw data ingested from the source.
3. notebooks/`03_generate_and_enhance_silver_data.ipynb` - generates silver data for data validation, which is the cleaned and transformed data. (enriched data)
4. notebooks/`04_generate_and_enhance_gold_data.ipynb` - generates gold data for data validation, which is the final, aggregated data ready for analysis.

## Running Data Quality checks from Jupyter notebooks

###TBA... 
