import random
from faker import Faker
from pathlib import Path
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from datetime import datetime, timedelta


PROJECT_ROOT = Path.cwd().parents[0]
DATA_PATH = PROJECT_ROOT / "data"

SOURCE_PATH = DATA_PATH / "source"
REFERENCE_PATH = DATA_PATH / "reference"
BRONZE_PATH = DATA_PATH / "bronze"
SILVER_PATH = DATA_PATH / "silver"
GOLD_PATH = DATA_PATH / "gold"


SEED = 58
fake = Faker()
Faker.seed(58)
random.seed(SEED)


def load_ids(
    path: Path,
    spark_connector: SparkSession,
    table_name: str, 
    id_column: str) -> list:
    
    try:
        df = spark_connector.read.format("delta").load(str(path / table_name))
        return df.select(id_column).rdd.flatMap(lambda x: x).collect()
    except Exception as e:
        print(f"Warning: Failed to load {table_name} ({e})")
        return []

def save_to_reference(
    df: DataFrame,
    table_name: str,
    path: Path = REFERENCE_PATH,
    mode: str = "overwrite") -> None:

    output_path = path / table_name

    (
        df.write
        .format("delta")
        .mode(mode)
        .save(str(output_path))
    )

    print(f"Saved to reference delta table: {output_path}")


def save_to_bronze(
    df: DataFrame,
    table_name: str,
    path: Path = BRONZE_PATH,
    mode: str = "overwrite") -> None:

    output_path = path / table_name

    (
        df.write
        .format("delta")
        .mode(mode)
        .save(str(output_path))
    )

    print(f"Saved to bronze layer delta table: {output_path}")


def save_to_silver(
    df: DataFrame,
    table_name: str,
    path: Path = SILVER_PATH,
    mode: str = "overwrite") -> None:

    output_path = path / table_name

    (
        df.write
        .format("delta")
        .mode(mode)
        .save(str(output_path))
    )

    print(f"Saved to silver layer delta table: {output_path}")


def save_to_gold(
    df: DataFrame,
    table_name: str,
    path: Path = GOLD_PATH,
    mode: str = "overwrite") -> None:

    output_path = path / table_name

    (
        df.write
        .format("delta")
        .mode(mode)
        .save(str(output_path))
    )

    print(f"Saved to gold layer delta table: {output_path}")


def generate_customers(
    num_customers: int,
    spark_connector: SparkSession) -> list:
    
    country_ids = load_ids(REFERENCE_PATH, spark_connector, "geography",'country_id')
    
    rows = []

    for customer_id in range(1, num_customers + 1):

        registration_date = fake.date_between(
            start_date="-2y",
            end_date="today"
        )

        rows.append((
            customer_id,
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            random.choice(country_ids),
            registration_date,
            datetime.utcnow(),
            "faker_python_library"
        ))

    return rows


def generate_employees(
    num_employees: int,
    spark_connector: SparkSession) -> list:

    country_ids = load_ids(REFERENCE_PATH, spark_connector, "geography",'country_id')
    
    rows = []

    for emp_id in range(1, num_employees + 1):

        first = fake.first_name()
        last = fake.last_name()
        email = fake.unique.email()
        phone = fake.phone_number()
        birth = fake.date_of_birth(minimum_age=18, maximum_age=65)
        hire = fake.date_between(start_date="-2y", end_date="-90d")
        country = random.choice(country_ids)

        rows.append((
            emp_id,
            first,
            last,
            email,
            phone,
            hire,
            birth,
            country,
            datetime.utcnow(),
            "faker_python_library"
        ))

    return rows


def generate_sales(
    num_sales: int, 
    spark_connector: SparkSession,):

    rows = []

    country_ids = load_ids(REFERENCE_PATH, spark_connector, "geography",'country_id')
    ga_ids = load_ids(REFERENCE_PATH, spark_connector, "google_analytics",'ga_id')
    delivery_ids = load_ids(REFERENCE_PATH, spark_connector, "delivery",'delivery_id')
    vendor_ids = load_ids(REFERENCE_PATH, spark_connector, "vendors",'vendor_id')
    games_ids = load_ids(BRONZE_PATH, spark_connector, "bgg_games", 'game_id')
    customer_ids = load_ids(BRONZE_PATH, spark_connector, "customers", 'customer_id')
    employee_ids = load_ids(BRONZE_PATH, spark_connector, "employees", 'employee_id')

    for sale_id in range(1, num_sales + 1):

        quantity = random.randint(1, 3)

        unit_cost = round(random.uniform(40.00, 90.00), 2)
        unit_price = round(random.uniform(44.99, 99.99), 2)

        # Ensure business logic: cost must be lower than price
        if unit_cost >= unit_price:
            unit_cost = round(unit_price * random.uniform(0.5, 0.8), 2)

        sale_time = fake.date_time_between(start_date="-1y", end_date="-1m")

        rows.append((
            sale_id,
            sale_time,
            random.choice(customer_ids),
            random.choice(games_ids),
            quantity,
            unit_cost,
            unit_price,
            "EUR", 
            random.choice(["CARD", "CASH", "TRANSFER"]),
            random.choice(delivery_ids),
            random.choice(employee_ids),
            random.choice(vendor_ids),
            random.choice(ga_ids),
            datetime.utcnow(),
            "faker_python_library"
        ))

    return rows
