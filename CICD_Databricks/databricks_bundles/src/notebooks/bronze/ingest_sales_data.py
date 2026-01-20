# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer: Sales Data Ingestion
# MAGIC 
# MAGIC This notebook ingests raw sales data from the landing zone into the bronze layer.
# MAGIC 
# MAGIC **Parameters:**
# MAGIC - `catalog`: Target catalog name
# MAGIC - `schema`: Target schema name

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

# Get widget parameters
dbutils.widgets.text("catalog", "bronze")
dbutils.widgets.text("schema", "raw_sales")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

print(f"Target: {catalog}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Schema

# COMMAND ----------

sales_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("transaction_date", TimestampType(), True),
    StructField("store_id", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("discount_amount", DoubleType(), True),
])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Ingest Data

# COMMAND ----------

# Define source path (landing zone volume)
source_path = f"/Volumes/{catalog}/{schema}/landing/sales/"

# Read raw data with schema enforcement
df_raw = (
    spark.read
    .format("json")
    .schema(sales_schema)
    .option("mode", "PERMISSIVE")
    .option("columnNameOfCorruptRecord", "_corrupt_record")
    .load(source_path)
)

# Add ingestion metadata
df_bronze = (
    df_raw
    .withColumn("_ingestion_timestamp", current_timestamp())
    .withColumn("_source_file", input_file_name())
    .withColumn("_batch_id", lit(spark.sparkContext.applicationId))
)

print(f"Records to ingest: {df_bronze.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Bronze Table

# COMMAND ----------

# Set catalog and schema
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")

# Write to bronze table with merge schema
(
    df_bronze
    .write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable("raw_sales_transactions")
)

print(f"Successfully ingested data to {catalog}.{schema}.raw_sales_transactions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log Ingestion Metrics

# COMMAND ----------

# Get table stats
table_stats = spark.sql("""
    SELECT 
        COUNT(*) as total_records,
        MIN(_ingestion_timestamp) as first_ingestion,
        MAX(_ingestion_timestamp) as last_ingestion
    FROM raw_sales_transactions
""").collect()[0]

print(f"Total records in table: {table_stats.total_records}")
print(f"First ingestion: {table_stats.first_ingestion}")
print(f"Last ingestion: {table_stats.last_ingestion}")

# Return success status
dbutils.notebook.exit("SUCCESS")
