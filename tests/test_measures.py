# tests/test_measures.py
import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import BIPipeline

class TestBusinessMeasures:
    """Test all 35+ business measures"""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline with sample data"""
        p = BIPipeline()
        p.load_data()
        return p
    
    def test_financial_measures(self, pipeline):
        """Test financial calculations"""
        measures = pipeline.calculate_all_measures()
        
        assert measures['total_revenue'] > 0
        assert measures['total_cost'] > 0
        assert measures['gross_profit'] >= 0
        assert 0 <= measures['gross_margin'] <= 100
        assert measures['total_profit'] >= 0
        assert 0 <= measures['profit_margin'] <= 100
    
    def test_sales_measures(self, pipeline):
        """Test sales calculations"""
        measures = pipeline.calculate_all_measures()
        
        assert measures['total_orders'] > 0
        assert measures['total_units_sold'] > 0
        assert measures['avg_order_value'] > 0
        assert measures['avg_unit_price'] > 0
        assert measures['unique_customers'] > 0
    
    def test_customer_measures(self, pipeline):
        """Test customer analytics"""
        measures = pipeline.calculate_all_measures()
        
        assert measures['customer_lifetime_value'] > 0
        assert 0 <= measures['repeat_purchase_rate'] <= 100
        assert measures['avg_purchase_frequency'] > 0
        assert 0 <= measures['churn_rate'] <= 100
    
    def test_time_intelligence(self, pipeline):
        """Test time-based calculations"""
        measures = pipeline.calculate_all_measures()
        
        assert measures['rolling_7d_avg'] >= 0
        assert measures['rolling_30d_avg'] >= 0
        assert measures['rolling_90d_avg'] >= 0
        assert measures['revenue_ytd'] >= 0
    
    def test_product_measures(self, pipeline):
        """Test product analytics"""
        measures = pipeline.calculate_all_measures()
        
        assert measures['total_products_available'] > 0
        assert measures['top_product_revenue'] > 0
        assert 0 <= measures['revenue_concentration'] <= 100
        assert measures['best_category_revenue_pct'] >= 0
    
    def test_measure_count(self, pipeline):
        """Test that we have 35+ measures"""
        measures = pipeline.calculate_all_measures()
        measure_count = len([k for k, v in measures.items() if not isinstance(v, dict)])
        
        assert measure_count >= 35
        print(f"\nTotal measures: {measure_count}")

def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "--tb=short"])

if __name__ == "__main__":
    run_tests()
