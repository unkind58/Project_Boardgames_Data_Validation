# Project_Boardgames_Data_Validation
This is BGG dataset enhanced with randomly generated data for data validation purposes

## Overview
This repository contains a dataset derived from BoardGameGeek (BGG) that has been enhanced with randomly generated data and Data Quality Framework (DQF) used to test this dataset.

The DQF is based on open-source tool 'Great Expectations' and provides the capability to ensure that data is loaded and processed correctly across various medallion layers.

It provides verification checks to validate data objects, aggregations, schemas, joins, data types, transformations and enrichment, while tracking key dataset characteristics over time, including row counts, null values, uniqueness, and referential integrity.

## Local Environment Setup
Below listed packages are required to set up the local environment.

- JupyterHub
- Python
- Poetry

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

## TBA...
