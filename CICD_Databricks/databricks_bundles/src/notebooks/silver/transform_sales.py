# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer: Sales Data Transformation
# MAGIC 
# MAGIC This notebook transforms raw sales data from bronze to cleaned silver layer.
# MAGIC 
# MAGIC **Transformations:**
# MAGIC - Data type casting and validation
# MAGIC - Null handling and default values
# MAGIC - Deduplication
# MAGIC - Business rule application

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, coalesce, lit, current_timestamp,
    trim, upper, lower, regexp_replace,
    to_date, date_format, year, month, dayofweek,
    round as spark_round
)
from pyspark.sql.window import Window
import pyspark.sql.functions as F

# Get widget parameters
dbutils.widgets.text("source_catalog", "bronze")
dbutils.widgets.text("target_catalog", "silver")

source_catalog = dbutils.widgets.get("source_catalog")
target_catalog = dbutils.widgets.get("target_catalog")

print(f"Source: {source_catalog}.raw_sales")
print(f"Target: {target_catalog}.cleaned_sales")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read Bronze Data

# COMMAND ----------

# Read from bronze layer
df_bronze = spark.table(f"{source_catalog}.raw_sales.raw_sales_transactions")

print(f"Bronze records: {df_bronze.count()}")
display(df_bronze.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Cleaning & Transformation

# COMMAND ----------

# Define cleaning transformations
df_cleaned = (
    df_bronze
    # Remove corrupt records
    .filter(col("_corrupt_record").isNull())
    
    # Clean string fields
    .withColumn("customer_id", trim(upper(col("customer_id"))))
    .withColumn("product_id", trim(upper(col("product_id"))))
    .withColumn("store_id", trim(upper(col("store_id"))))
    .withColumn("payment_method", trim(lower(col("payment_method"))))
    
    # Handle nulls with defaults
    .withColumn("quantity", coalesce(col("quantity"), lit(1)))
    .withColumn("unit_price", coalesce(col("unit_price"), lit(0.0)))
    .withColumn("discount_amount", coalesce(col("discount_amount"), lit(0.0)))
    
    # Calculate derived fields
    .withColumn("gross_amount", spark_round(col("quantity") * col("unit_price"), 2))
    .withColumn("net_amount", spark_round(col("gross_amount") - col("discount_amount"), 2))
    
    # Add date dimensions
    .withColumn("transaction_date_only", to_date(col("transaction_date")))
    .withColumn("transaction_year", year(col("transaction_date")))
    .withColumn("transaction_month", month(col("transaction_date")))
    .withColumn("transaction_day_of_week", dayofweek(col("transaction_date")))
    
    # Add processing metadata
    .withColumn("_processed_timestamp", current_timestamp())
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deduplication

# COMMAND ----------

# Deduplicate based on transaction_id, keeping the latest ingestion
window_spec = Window.partitionBy("transaction_id").orderBy(col("_ingestion_timestamp").desc())

df_deduped = (
    df_cleaned
    .withColumn("_row_num", F.row_number().over(window_spec))
    .filter(col("_row_num") == 1)
    .drop("_row_num", "_corrupt_record")
)

print(f"Records after deduplication: {df_deduped.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

# Basic quality checks
quality_checks = {
    "total_records": df_deduped.count(),
    "null_customer_ids": df_deduped.filter(col("customer_id").isNull()).count(),
    "negative_amounts": df_deduped.filter(col("net_amount") < 0).count(),
    "future_dates": df_deduped.filter(col("transaction_date") > current_timestamp()).count(),
}

print("Quality Check Results:")
for check, value in quality_checks.items():
    status = "PASS" if (check == "total_records" or value == 0) else "WARNING"
    print(f"  {check}: {value} [{status}]")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Silver Table

# COMMAND ----------

# Select final columns
df_silver = df_deduped.select(
    "transaction_id",
    "customer_id",
    "product_id",
    "store_id",
    "transaction_date",
    "transaction_date_only",
    "transaction_year",
    "transaction_month",
    "transaction_day_of_week",
    "quantity",
    "unit_price",
    "discount_amount",
    "gross_amount",
    "net_amount",
    "payment_method",
    "_ingestion_timestamp",
    "_processed_timestamp",
    "_source_file"
)

# Write to silver table using merge
spark.sql(f"USE CATALOG {target_catalog}")
spark.sql("USE SCHEMA cleaned_sales")

# Create table if not exists, then merge
df_silver.createOrReplaceTempView("silver_updates")

spark.sql("""
    MERGE INTO sales_transactions AS target
    USING silver_updates AS source
    ON target.transaction_id = source.transaction_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

print(f"Successfully transformed data to {target_catalog}.cleaned_sales.sales_transactions")

# COMMAND ----------

dbutils.notebook.exit("SUCCESS")
