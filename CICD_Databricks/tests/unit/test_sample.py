# =============================================================================
# Unit Tests - Sample Test Suite
# =============================================================================
"""
Sample unit tests demonstrating testing patterns for Databricks transformations.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


# =============================================================================
# Test: String Cleaning Functions
# =============================================================================

class TestStringCleaning:
    """Tests for string cleaning transformation functions."""
    
    def test_clean_string_trims_whitespace(self, clean_string_udf):
        """Verify that leading/trailing whitespace is removed."""
        assert clean_string_udf("  hello  ") == "HELLO"
    
    def test_clean_string_converts_to_uppercase(self, clean_string_udf):
        """Verify that strings are converted to uppercase."""
        assert clean_string_udf("hello world") == "HELLO WORLD"
    
    def test_clean_string_handles_none(self, clean_string_udf):
        """Verify that None values are handled gracefully."""
        assert clean_string_udf(None) is None
    
    def test_clean_string_handles_empty(self, clean_string_udf):
        """Verify that empty strings are handled correctly."""
        assert clean_string_udf("") == ""


# =============================================================================
# Test: Amount Calculations
# =============================================================================

class TestAmountCalculations:
    """Tests for financial calculation functions."""
    
    def test_calculate_net_amount_basic(self, calculate_net_amount):
        """Verify basic net amount calculation."""
        result = calculate_net_amount(quantity=2, unit_price=100.0, discount=10.0)
        assert result == 190.0
    
    def test_calculate_net_amount_no_discount(self, calculate_net_amount):
        """Verify calculation when no discount is applied."""
        result = calculate_net_amount(quantity=3, unit_price=50.0, discount=0)
        assert result == 150.0
    
    def test_calculate_net_amount_null_discount(self, calculate_net_amount):
        """Verify calculation when discount is None."""
        result = calculate_net_amount(quantity=1, unit_price=99.99, discount=None)
        assert result == 99.99
    
    def test_calculate_net_amount_rounding(self, calculate_net_amount):
        """Verify that amounts are rounded to 2 decimal places."""
        result = calculate_net_amount(quantity=3, unit_price=33.333, discount=0)
        assert result == 100.0  # Rounded from 99.999


# =============================================================================
# Test: Data Validation
# =============================================================================

class TestDataValidation:
    """Tests for data validation functions."""
    
    @pytest.mark.unit
    def test_valid_transaction_id_format(self):
        """Verify transaction ID format validation."""
        valid_ids = ["TXN000001", "TXN123456", "TXN999999"]
        for txn_id in valid_ids:
            assert txn_id.startswith("TXN")
            assert len(txn_id) == 9
    
    @pytest.mark.unit
    def test_valid_customer_id_format(self):
        """Verify customer ID format validation."""
        valid_ids = ["CUST0001", "CUST9999"]
        for cust_id in valid_ids:
            assert cust_id.startswith("CUST")
            assert len(cust_id) == 8
    
    @pytest.mark.unit
    def test_quantity_must_be_positive(self):
        """Verify that quantity validation works."""
        def validate_quantity(qty):
            return qty is not None and qty > 0
        
        assert validate_quantity(1) is True
        assert validate_quantity(100) is True
        assert validate_quantity(0) is False
        assert validate_quantity(-1) is False
        assert validate_quantity(None) is False


# =============================================================================
# Test: Spark DataFrame Transformations
# =============================================================================

@pytest.mark.integration
class TestSparkTransformations:
    """Integration tests for Spark DataFrame transformations."""
    
    def test_create_sample_dataframe(self, sample_sales_dataframe):
        """Verify sample DataFrame creation."""
        df = sample_sales_dataframe(10)
        assert df.count() == 10
    
    def test_dataframe_has_required_columns(self, sample_sales_dataframe):
        """Verify DataFrame has all required columns."""
        df = sample_sales_dataframe(1)
        required_columns = [
            "transaction_id", "customer_id", "product_id",
            "quantity", "unit_price", "discount_amount"
        ]
        for col in required_columns:
            assert col in df.columns
    
    def test_filter_positive_quantities(self, spark_session, sample_sales_dataframe):
        """Test filtering for positive quantities."""
        df = sample_sales_dataframe(100)
        filtered = df.filter("quantity > 0")
        assert filtered.count() == df.count()  # All should be positive
    
    def test_aggregation_by_store(self, spark_session, sample_sales_dataframe):
        """Test aggregation by store_id."""
        df = sample_sales_dataframe(100)
        agg_df = df.groupBy("store_id").count()
        assert agg_df.count() > 0
        assert agg_df.count() <= 10  # Max 10 stores in sample data


# =============================================================================
# Test: Data Quality Checks
# =============================================================================

@pytest.mark.dqx
class TestDataQuality:
    """Tests for data quality check functions."""
    
    def test_null_check(self, sample_sales_data):
        """Verify null detection in data."""
        data = sample_sales_data(10)
        # Add a null record
        data.append({
            "transaction_id": None,
            "customer_id": "CUST0001",
            "product_id": "PROD0001",
            "quantity": 1,
            "unit_price": 10.0,
            "transaction_date": datetime.now().isoformat(),
            "store_id": "STORE01",
            "payment_method": "cash",
            "discount_amount": 0
        })
        
        null_count = sum(1 for d in data if d["transaction_id"] is None)
        assert null_count == 1
    
    def test_duplicate_detection(self, sample_sales_data):
        """Verify duplicate detection logic."""
        data = sample_sales_data(10)
        # Add a duplicate
        data.append(data[0].copy())
        
        transaction_ids = [d["transaction_id"] for d in data]
        unique_ids = set(transaction_ids)
        
        assert len(transaction_ids) > len(unique_ids)  # Duplicates exist
    
    def test_date_range_validation(self, sample_sales_data):
        """Verify date range validation."""
        data = sample_sales_data(10)
        
        for record in data:
            date_str = record["transaction_date"]
            record_date = datetime.fromisoformat(date_str)
            # All dates should be in the past year
            assert record_date <= datetime.now()
            assert record_date >= datetime.now() - timedelta(days=366)


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    @pytest.mark.unit
    def test_empty_dataframe_handling(self, spark_session):
        """Verify handling of empty DataFrames."""
        from pyspark.sql.types import StructType, StructField, StringType
        
        schema = StructType([
            StructField("id", StringType(), True),
            StructField("value", StringType(), True)
        ])
        
        empty_df = spark_session.createDataFrame([], schema)
        assert empty_df.count() == 0
        assert len(empty_df.columns) == 2
    
    @pytest.mark.unit
    def test_very_large_quantity(self, calculate_net_amount):
        """Verify handling of very large quantities."""
        result = calculate_net_amount(quantity=1000000, unit_price=0.01, discount=0)
        assert result == 10000.0
    
    @pytest.mark.unit
    def test_zero_price_handling(self, calculate_net_amount):
        """Verify handling of zero prices."""
        result = calculate_net_amount(quantity=10, unit_price=0, discount=0)
        assert result == 0.0


# Import timedelta for date tests
from datetime import timedelta
