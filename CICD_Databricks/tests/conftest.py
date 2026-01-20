# =============================================================================
# Pytest Fixtures and Configuration
# =============================================================================
"""
Shared pytest fixtures for unit and integration testing.
Provides mock Spark sessions, sample data, and common utilities.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import random
import string


# =============================================================================
# Spark Session Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def spark_session():
    """
    Creates a local Spark session for testing.
    Uses memory-based storage to avoid file system dependencies.
    """
    try:
        from pyspark.sql import SparkSession
        
        spark = (
            SparkSession.builder
            .master("local[2]")
            .appName("pytest-databricks-cicd")
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
            .config("spark.driver.memory", "2g")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.default.parallelism", "2")
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .getOrCreate()
        )
        
        # Set log level to reduce noise
        spark.sparkContext.setLogLevel("WARN")
        
        yield spark
        
        spark.stop()
        
    except ImportError:
        # If PySpark is not available, provide a mock
        yield MagicMock()


@pytest.fixture
def mock_spark():
    """
    Provides a mock Spark session for pure unit tests.
    """
    mock_session = MagicMock()
    mock_session.sql.return_value = MagicMock()
    mock_session.table.return_value = MagicMock()
    mock_session.read.return_value = MagicMock()
    return mock_session


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_sales_data():
    """
    Generates sample sales transaction data for testing.
    """
    def _generate(num_records=100):
        data = []
        for i in range(num_records):
            data.append({
                "transaction_id": f"TXN{i:06d}",
                "customer_id": f"CUST{random.randint(1, 100):04d}",
                "product_id": f"PROD{random.randint(1, 50):04d}",
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(10.0, 500.0), 2),
                "transaction_date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                "store_id": f"STORE{random.randint(1, 10):02d}",
                "payment_method": random.choice(["credit_card", "debit_card", "cash", "mobile"]),
                "discount_amount": round(random.uniform(0, 50.0), 2)
            })
        return data
    
    return _generate


@pytest.fixture
def sample_sales_dataframe(spark_session, sample_sales_data):
    """
    Creates a Spark DataFrame with sample sales data.
    """
    def _create(num_records=100):
        data = sample_sales_data(num_records)
        return spark_session.createDataFrame(data)
    
    return _create


@pytest.fixture
def sample_customer_data():
    """
    Generates sample customer data for testing.
    """
    def _generate(num_customers=50):
        data = []
        for i in range(num_customers):
            data.append({
                "customer_id": f"CUST{i:04d}",
                "customer_name": f"Customer {i}",
                "email": f"customer{i}@example.com",
                "registration_date": (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                "customer_segment": random.choice(["premium", "standard", "basic"]),
                "country": random.choice(["IT", "DE", "FR", "ES", "UK"])
            })
        return data
    
    return _generate


# =============================================================================
# Databricks Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_dbutils():
    """
    Mocks the Databricks dbutils object.
    """
    mock = MagicMock()
    mock.widgets.get.return_value = "test_value"
    mock.notebook.exit.return_value = None
    mock.fs.ls.return_value = []
    return mock


@pytest.fixture
def mock_catalog_context():
    """
    Provides a mock Unity Catalog context for testing.
    """
    return {
        "catalog": "test_catalog",
        "schema": "test_schema",
        "environment": "dev"
    }


# =============================================================================
# Transformation Function Fixtures
# =============================================================================

@pytest.fixture
def clean_string_udf():
    """
    Provides the string cleaning function for testing.
    """
    def clean_string(value):
        if value is None:
            return None
        return value.strip().upper()
    
    return clean_string


@pytest.fixture
def calculate_net_amount():
    """
    Provides the net amount calculation function for testing.
    """
    def calc(quantity, unit_price, discount):
        gross = quantity * unit_price
        return round(gross - (discount or 0), 2)
    
    return calc


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture(scope="session")
def test_config():
    """
    Provides test configuration values.
    """
    return {
        "bronze_catalog": "test_bronze",
        "silver_catalog": "test_silver",
        "gold_catalog": "test_gold",
        "test_schema": "test_data",
        "max_records": 1000
    }


# =============================================================================
# Cleanup Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_temp_tables(spark_session):
    """
    Automatically cleans up temporary tables after each test.
    """
    yield
    
    # Cleanup logic
    try:
        for table in spark_session.catalog.listTables():
            if table.isTemporary:
                spark_session.catalog.dropTempView(table.name)
    except Exception:
        pass  # Ignore cleanup errors
