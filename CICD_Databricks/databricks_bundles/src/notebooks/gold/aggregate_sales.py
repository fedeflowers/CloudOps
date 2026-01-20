# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer: Sales Aggregations
# MAGIC 
# MAGIC This notebook creates business-ready aggregated views from silver data.
# MAGIC 
# MAGIC **Aggregations:**
# MAGIC - Daily sales summary
# MAGIC - Product performance metrics
# MAGIC - Store performance metrics
# MAGIC - Customer lifetime value

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, count, avg, min as spark_min, max as spark_max,
    countDistinct, current_timestamp, round as spark_round,
    first, last, datediff, lit
)
from pyspark.sql.window import Window

# Get widget parameters
dbutils.widgets.text("source_catalog", "silver")
dbutils.widgets.text("target_catalog", "gold")

source_catalog = dbutils.widgets.get("source_catalog")
target_catalog = dbutils.widgets.get("target_catalog")

print(f"Source: {source_catalog}.cleaned_sales")
print(f"Target: {target_catalog}.analytics")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read Silver Data

# COMMAND ----------

df_silver = spark.table(f"{source_catalog}.cleaned_sales.sales_transactions")
print(f"Silver records: {df_silver.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Daily Sales Summary

# COMMAND ----------

df_daily_sales = (
    df_silver
    .groupBy("transaction_date_only", "store_id")
    .agg(
        count("transaction_id").alias("transaction_count"),
        spark_sum("quantity").alias("total_quantity"),
        spark_round(spark_sum("gross_amount"), 2).alias("gross_revenue"),
        spark_round(spark_sum("discount_amount"), 2).alias("total_discounts"),
        spark_round(spark_sum("net_amount"), 2).alias("net_revenue"),
        countDistinct("customer_id").alias("unique_customers"),
        countDistinct("product_id").alias("unique_products"),
        spark_round(avg("net_amount"), 2).alias("avg_transaction_value")
    )
    .withColumn("_aggregated_timestamp", current_timestamp())
)

print(f"Daily sales records: {df_daily_sales.count()}")

# Write to gold table
spark.sql(f"USE CATALOG {target_catalog}")
spark.sql("USE SCHEMA analytics")

(
    df_daily_sales
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("daily_sales_summary")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Product Performance

# COMMAND ----------

df_product_performance = (
    df_silver
    .groupBy("product_id", "transaction_year", "transaction_month")
    .agg(
        count("transaction_id").alias("transaction_count"),
        spark_sum("quantity").alias("total_quantity_sold"),
        spark_round(spark_sum("net_amount"), 2).alias("total_revenue"),
        spark_round(avg("unit_price"), 2).alias("avg_unit_price"),
        spark_round(avg("discount_amount"), 2).alias("avg_discount"),
        countDistinct("customer_id").alias("unique_customers"),
        countDistinct("store_id").alias("stores_sold_in")
    )
    .withColumn("_aggregated_timestamp", current_timestamp())
)

(
    df_product_performance
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("product_performance")
)

print("Product performance table created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Store Performance

# COMMAND ----------

df_store_performance = (
    df_silver
    .groupBy("store_id", "transaction_year", "transaction_month")
    .agg(
        count("transaction_id").alias("transaction_count"),
        spark_round(spark_sum("net_amount"), 2).alias("total_revenue"),
        spark_round(avg("net_amount"), 2).alias("avg_transaction_value"),
        countDistinct("customer_id").alias("unique_customers"),
        countDistinct("product_id").alias("products_sold"),
        spark_round(spark_sum("discount_amount"), 2).alias("total_discounts_given")
    )
    .withColumn("revenue_per_customer", spark_round(col("total_revenue") / col("unique_customers"), 2))
    .withColumn("_aggregated_timestamp", current_timestamp())
)

(
    df_store_performance
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("store_performance")
)

print("Store performance table created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Customer Lifetime Value

# COMMAND ----------

# Customer-level aggregations
df_customer_ltv = (
    df_silver
    .groupBy("customer_id")
    .agg(
        count("transaction_id").alias("total_transactions"),
        spark_sum("quantity").alias("total_items_purchased"),
        spark_round(spark_sum("net_amount"), 2).alias("lifetime_value"),
        spark_round(avg("net_amount"), 2).alias("avg_transaction_value"),
        spark_min("transaction_date").alias("first_purchase_date"),
        spark_max("transaction_date").alias("last_purchase_date"),
        countDistinct("product_id").alias("unique_products_purchased"),
        countDistinct("store_id").alias("stores_visited")
    )
    .withColumn("customer_tenure_days", 
                datediff(col("last_purchase_date"), col("first_purchase_date")))
    .withColumn("purchase_frequency", 
                spark_round(col("total_transactions") / (col("customer_tenure_days") + 1), 4))
    .withColumn("_aggregated_timestamp", current_timestamp())
)

(
    df_customer_ltv
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("customer_lifetime_value")
)

print("Customer LTV table created")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

# Print summary of created tables
tables = ["daily_sales_summary", "product_performance", "store_performance", "customer_lifetime_value"]

print("=" * 60)
print("Gold Layer Tables Created:")
print("=" * 60)

for table in tables:
    count = spark.table(table).count()
    print(f"  {target_catalog}.analytics.{table}: {count:,} records")

print("=" * 60)

dbutils.notebook.exit("SUCCESS")
