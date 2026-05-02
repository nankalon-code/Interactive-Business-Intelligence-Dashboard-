# src/pipeline.py
import pandas as pd
import numpy as np
import os
import sqlite3
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class BIPipeline:
    """Complete BI pipeline with 6 data sources and 35+ measures"""
    
    def __init__(self, data_path='data/'):
        self.data_path = data_path
        self.orders = None
        self.customers = None
        self.products = None
        self.marketing = None
        self.inventory = None
        self.returns = None
        self.results = {}
        self.optimized_views = {}
        
    def load_data(self):
        """Load all 6 data sources"""
        print("Loading data sources...")
        
        self.orders = pd.read_csv(os.path.join(self.data_path, 'orders.csv'))
        self.customers = pd.read_csv(os.path.join(self.data_path, 'customers.csv'))
        self.products = pd.read_csv(os.path.join(self.data_path, 'products.csv'))
        self.marketing = pd.read_csv(os.path.join(self.data_path, 'marketing.csv'))
        self.inventory = pd.read_csv(os.path.join(self.data_path, 'inventory.csv'))
        self.returns = pd.read_csv(os.path.join(self.data_path, 'returns.csv'))
        
        # Convert date columns
        self.orders['order_date'] = pd.to_datetime(self.orders['order_date'])
        self.orders['order_timestamp'] = pd.to_datetime(self.orders['order_timestamp'])
        self.customers['signup_date'] = pd.to_datetime(self.customers['signup_date'])
        self.marketing['date'] = pd.to_datetime(self.marketing['date'])
        self.inventory['date'] = pd.to_datetime(self.inventory['date'])
        self.returns['return_date'] = pd.to_datetime(self.returns['return_date'])
        
        print(f"   Loaded {len(self.orders):,} orders")
        print(f"   Loaded {len(self.customers):,} customers")
        print(f"   Loaded {len(self.products)} products")
        print(f"   Loaded {len(self.marketing):,} marketing records")
        print(f"   Loaded {len(self.inventory):,} inventory records")
        print(f"   Loaded {len(self.returns):,} returns")
    
    def create_star_schema(self):
        """Build star schema with fact and dimension tables"""
        print("\nCreating star schema...")
        
        # Dimension: Customer
        dim_customer = self.customers[['customer_id', 'customer_name', 'segment', 'region']].copy()
        
        # Dimension: Product
        dim_product = self.products[['product_id', 'product_name', 'category', 'subcategory', 'selling_price']].copy()
        
        # Dimension: Date
        dates = pd.DataFrame({'order_date': self.orders['order_date'].unique()})
        dates['date_key'] = dates['order_date'].dt.strftime('%Y%m%d').astype(int)
        dates['year'] = dates['order_date'].dt.year
        dates['quarter'] = dates['order_date'].dt.quarter
        dates['month'] = dates['order_date'].dt.month
        dates['month_name'] = dates['order_date'].dt.strftime('%B')
        dates['week'] = dates['order_date'].dt.isocalendar().week
        dates['day_of_week'] = dates['order_date'].dt.dayofweek
        dates['is_weekend'] = (dates['day_of_week'] >= 5).astype(int)
        
        # Fact: Orders
        fact_orders = self.orders.copy()
        fact_orders['date_key'] = fact_orders['order_date'].dt.strftime('%Y%m%d').astype(int)
        fact_orders['net_revenue'] = fact_orders['revenue'] - fact_orders['discount']
        
        # Save star schema
        dim_customer.to_csv('data/dim_customer.csv', index=False)
        dim_product.to_csv('data/dim_product.csv', index=False)
        dates.to_csv('data/dim_date.csv', index=False)
        fact_orders.to_csv('data/fact_orders.csv', index=False)
        
        # Store for later use
        self.dim_customer = dim_customer
        self.dim_product = dim_product
        self.dim_date = dates
        self.fact_orders = fact_orders
        
        print(f"   Created: fact_orders ({len(fact_orders):,} records)")
        print(f"   Created: dim_customer ({len(dim_customer):,} records)")
        print(f"   Created: dim_product ({len(dim_product)} records)")
        print(f"   Created: dim_date ({len(dates)} records)")
    
    def calculate_all_measures(self) -> Dict[str, Any]:
        """Calculate 35+ business measures"""
        print("\nCalculating 35+ business measures...")
        
        measures = {}
        
        # ============================================
        # FINANCIAL MEASURES (8)
        # ============================================
        measures['total_revenue'] = float(self.orders['revenue'].sum())
        measures['total_cost'] = float(self.orders['cost'].sum())
        measures['total_discount'] = float(self.orders['discount'].sum())
        measures['net_revenue'] = measures['total_revenue'] - measures['total_discount']
        measures['gross_profit'] = measures['total_revenue'] - measures['total_cost']
        measures['gross_margin'] = (measures['gross_profit'] / measures['total_revenue']) * 100 if measures['total_revenue'] > 0 else 0
        measures['total_profit'] = float(self.orders['profit'].sum())
        measures['profit_margin'] = (measures['total_profit'] / measures['total_revenue']) * 100 if measures['total_revenue'] > 0 else 0
        
        # ============================================
        # SALES MEASURES (7)
        # ============================================
        measures['total_orders'] = int(len(self.orders))
        measures['total_units_sold'] = int(self.orders['quantity'].sum())
        measures['avg_order_value'] = measures['total_revenue'] / measures['total_orders'] if measures['total_orders'] > 0 else 0
        measures['avg_unit_price'] = measures['total_revenue'] / measures['total_units_sold'] if measures['total_units_sold'] > 0 else 0
        measures['avg_items_per_order'] = measures['total_units_sold'] / measures['total_orders'] if measures['total_orders'] > 0 else 0
        measures['unique_customers'] = int(self.orders['customer_id'].nunique())
        measures['unique_products_sold'] = int(self.orders['product_id'].nunique())
        
        # ============================================
        # CUSTOMER MEASURES (8)
        # ============================================
        measures['customer_lifetime_value'] = measures['total_revenue'] / measures['unique_customers'] if measures['unique_customers'] > 0 else 0
        
        # Repeat purchase rate
        customer_orders = self.orders.groupby('customer_id').size()
        repeat_customers = (customer_orders > 1).sum()
        measures['repeat_purchase_rate'] = (repeat_customers / measures['unique_customers']) * 100 if measures['unique_customers'] > 0 else 0
        
        # Average purchase frequency
        measures['avg_purchase_frequency'] = float(customer_orders.mean()) if len(customer_orders) > 0 else 0
        
        # Customer acquisition cost
        total_marketing_spend = float(self.marketing['spend'].sum()) if self.marketing is not None else 0
        measures['customer_acquisition_cost'] = total_marketing_spend / measures['unique_customers'] if measures['unique_customers'] > 0 else 0
        
        # New vs returning (last 30 days)
        today = datetime.now()
        last_30_days = today - timedelta(days=30)
        recent_orders = self.orders[self.orders['order_date'] >= last_30_days]
        recent_customers = recent_orders['customer_id'].unique()
        first_orders = self.orders.groupby('customer_id')['order_date'].min()
        new_customers = [c for c in recent_customers if first_orders.get(c, today) >= last_30_days]
        measures['new_customers_last_30d'] = int(len(new_customers))
        measures['returning_customers_last_30d'] = int(len(recent_customers) - len(new_customers))
        
        # Churn rate (no purchase in 90 days)
        last_orders = self.orders.groupby('customer_id')['order_date'].max()
        churned = (last_orders < (today - timedelta(days=90))).sum()
        measures['churn_rate'] = (churned / measures['unique_customers']) * 100 if measures['unique_customers'] > 0 else 0
        
        # ============================================
        # TIME INTELLIGENCE MEASURES (9)
        # ============================================
        self.orders['year_month'] = self.orders['order_date'].dt.to_period('M')
        monthly_revenue = self.orders.groupby('year_month')['revenue'].sum()
        
        # Year over Year growth
        if len(monthly_revenue) >= 12:
            last_12m = monthly_revenue.iloc[-12:].sum()
            previous_12m = monthly_revenue.iloc[-24:-12].sum() if len(monthly_revenue) >= 24 else last_12m
            measures['revenue_yoy_growth'] = ((last_12m - previous_12m) / previous_12m) * 100 if previous_12m > 0 else 0
        else:
            measures['revenue_yoy_growth'] = 0.0
        
        # Month over Month growth
        if len(monthly_revenue) >= 2:
            current_month = monthly_revenue.iloc[-1]
            previous_month = monthly_revenue.iloc[-2]
            measures['revenue_mom_growth'] = ((current_month - previous_month) / previous_month) * 100 if previous_month > 0 else 0
        else:
            measures['revenue_mom_growth'] = 0.0
        
        # Rolling averages (7, 30, 90 days)
        daily_revenue = self.orders.groupby('order_date')['revenue'].sum()
        measures['rolling_7d_avg'] = float(daily_revenue.tail(7).mean()) if len(daily_revenue) >= 7 else 0
        measures['rolling_30d_avg'] = float(daily_revenue.tail(30).mean()) if len(daily_revenue) >= 30 else 0
        measures['rolling_90d_avg'] = float(daily_revenue.tail(90).mean()) if len(daily_revenue) >= 90 else 0
        
        # Year to Date
        current_year = datetime.now().year
        ytd_orders = self.orders[self.orders['order_date'].dt.year == current_year]
        measures['revenue_ytd'] = float(ytd_orders['revenue'].sum())
        measures['orders_ytd'] = int(len(ytd_orders))
        
        # Previous Year to Date
        last_year_ytd = self.orders[
            (self.orders['order_date'].dt.year == current_year - 1) &
            (self.orders['order_date'].dt.dayofyear <= datetime.now().timetuple().tm_yday)
        ]
        measures['revenue_pytd'] = float(last_year_ytd['revenue'].sum()) if len(last_year_ytd) > 0 else 0
        
        # ============================================
        # PRODUCT MEASURES (6)
        # ============================================
        product_revenue = self.orders.groupby('product_id')['revenue'].sum()
        measures['total_products_available'] = int(len(self.products))
        measures['top_product_revenue'] = float(product_revenue.max()) if len(product_revenue) > 0 else 0
        measures['top_product_id'] = int(product_revenue.idxmax()) if len(product_revenue) > 0 else 0
        
        # Pareto (80/20) analysis
        if len(product_revenue) > 0:
            sorted_revenue = product_revenue.sort_values(ascending=False)
            cumulative = sorted_revenue.cumsum()
            pareto_threshold = measures['total_revenue'] * 0.8
            products_for_80 = (cumulative <= pareto_threshold).sum()
            measures['pareto_80_20_ratio'] = (products_for_80 / len(product_revenue)) * 100
        else:
            measures['pareto_80_20_ratio'] = 0
        
        # Top 10% concentration
        if len(product_revenue) > 0:
            top_10_percent = int(len(product_revenue) * 0.1)
            if top_10_percent > 0:
                top_10_revenue = product_revenue.nlargest(top_10_percent).sum()
                measures['top_10_percent_revenue'] = float(top_10_revenue)
                measures['revenue_concentration'] = (top_10_revenue / measures['total_revenue']) * 100 if measures['total_revenue'] > 0 else 0
            else:
                measures['top_10_percent_revenue'] = 0
                measures['revenue_concentration'] = 0
        else:
            measures['top_10_percent_revenue'] = 0
            measures['revenue_concentration'] = 0
        
        # Category performance
        orders_with_cat = self.orders.merge(self.products[['product_id', 'category']], on='product_id')
        category_revenue = orders_with_cat.groupby('category')['revenue'].sum()
        if len(category_revenue) > 0:
            measures['best_category'] = str(category_revenue.idxmax())
            measures['best_category_revenue_pct'] = (category_revenue.max() / measures['total_revenue']) * 100 if measures['total_revenue'] > 0 else 0
        else:
            measures['best_category'] = "Unknown"
            measures['best_category_revenue_pct'] = 0
        measures['category_count'] = int(len(category_revenue))
        
        # ============================================
        # SEGMENT MEASURES (5)
        # ============================================
        orders_with_seg = self.orders.merge(self.customers[['customer_id', 'segment']], on='customer_id')
        segment_revenue = orders_with_seg.groupby('segment')['revenue'].sum()
        total_rev = measures['total_revenue']
        
        measures['premium_segment_revenue_pct'] = float((segment_revenue.get('Premium', 0) / total_rev) * 100) if total_rev > 0 else 0
        measures['gold_segment_revenue_pct'] = float((segment_revenue.get('Gold', 0) / total_rev) * 100) if total_rev > 0 else 0
        measures['silver_segment_revenue_pct'] = float((segment_revenue.get('Silver', 0) / total_rev) * 100) if total_rev > 0 else 0
        measures['bronze_segment_revenue_pct'] = float((segment_revenue.get('Bronze', 0) / total_rev) * 100) if total_rev > 0 else 0
        
        # Segment average order value
        segment_aov = orders_with_seg.groupby('segment')['revenue'].mean()
        measures['premium_aov'] = float(segment_aov.get('Premium', 0))
        
        # ============================================
        # OPERATIONAL MEASURES (5)
        # ============================================
        measures['avg_daily_revenue'] = measures['total_revenue'] / self.orders['order_date'].nunique() if self.orders['order_date'].nunique() > 0 else 0
        
        # Peak hour analysis
        self.orders['hour'] = self.orders['order_timestamp'].dt.hour
        hourly_orders = self.orders.groupby('hour')['order_id'].count()
        if len(hourly_orders) > 0:
            measures['peak_order_hour'] = int(hourly_orders.idxmax())
            measures['peak_hour_volume'] = int(hourly_orders.max())
        else:
            measures['peak_order_hour'] = 0
            measures['peak_hour_volume'] = 0
        
        # Weekend vs weekday performance
        self.orders['is_weekend'] = self.orders['order_date'].dt.dayofweek >= 5
        weekend_revenue = self.orders[self.orders['is_weekend']]['revenue'].sum()
        measures['weekend_revenue_pct'] = float((weekend_revenue / measures['total_revenue']) * 100) if measures['total_revenue'] > 0 else 0
        
        # Best month
        monthly_performance = self.orders.groupby(self.orders['order_date'].dt.month)['revenue'].sum()
        if len(monthly_performance) > 0:
            measures['best_month'] = int(monthly_performance.idxmax())
            measures['best_month_revenue'] = float(monthly_performance.max())
        else:
            measures['best_month'] = 0
            measures['best_month_revenue'] = 0
        
        # Seasonality factor
        if len(monthly_performance) > 0:
            peak_month_avg = monthly_performance.max()
            avg_monthly = monthly_performance.mean()
            measures['seasonality_factor'] = peak_month_avg / avg_monthly if avg_monthly > 0 else 1
        else:
            measures['seasonality_factor'] = 1.0
        
        # ============================================
        # INVENTORY MEASURES (3)
        # ============================================
        if self.inventory is not None and len(self.inventory) > 0:
            avg_stock = self.inventory.groupby('product_id')['stock_level'].mean()
            product_costs = self.products.set_index('product_id')['cost_price']
            measures['avg_inventory_value'] = float((avg_stock * product_costs).sum())
            measures['stockout_rate'] = float((self.inventory['stock_level'] == 0).mean() * 100)
            measures['inventory_turnover'] = measures['total_units_sold'] / avg_stock.mean() if avg_stock.mean() > 0 else 0
        else:
            measures['avg_inventory_value'] = 0.0
            measures['stockout_rate'] = 0.0
            measures['inventory_turnover'] = 0.0
        
        # ============================================
        # RETURN MEASURES (2 - skip dict)
        # ============================================
        if self.returns is not None and len(self.returns) > 0:
            measures['total_return_amount'] = float(self.returns['refund_amount'].sum())
            measures['return_rate'] = (len(self.returns) / len(self.orders)) * 100 if len(self.orders) > 0 else 0
            # Skip return_rate_by_reason because it's a dict
        else:
            measures['total_return_amount'] = 0.0
            measures['return_rate'] = 0.0
        
        # ============================================
        # MARKETING MEASURES (3)
        # ============================================
        if self.marketing is not None and len(self.marketing) > 0:
            measures['total_marketing_spend'] = float(self.marketing['spend'].sum())
            if measures['total_marketing_spend'] > 0:
                measures['marketing_roi'] = ((measures['total_revenue'] - measures['total_marketing_spend']) / measures['total_marketing_spend']) * 100
            else:
                measures['marketing_roi'] = 0.0
            measures['cac_ltv_ratio'] = measures['customer_acquisition_cost'] / measures['customer_lifetime_value'] if measures['customer_lifetime_value'] > 0 else 0
        else:
            measures['total_marketing_spend'] = 0.0
            measures['marketing_roi'] = 0.0
            measures['cac_ltv_ratio'] = 0.0
        
        # ============================================
        # COHORT MEASURES (3)
        # ============================================
        # Customer cohorts by signup month
        self.customers['cohort_month'] = self.customers['signup_date'].dt.to_period('M')
        cohort_sizes = self.customers.groupby('cohort_month')['customer_id'].count()
        measures['total_cohorts'] = int(len(cohort_sizes))
        if len(cohort_sizes) > 0:
            measures['largest_cohort'] = str(cohort_sizes.idxmax())
            measures['largest_cohort_size'] = int(cohort_sizes.max())
        else:
            measures['largest_cohort'] = "Unknown"
            measures['largest_cohort_size'] = 0
        
        self.results = measures
        
        # Count measures (excluding dicts)
        measure_count = len([k for k, v in measures.items() if not isinstance(v, dict)])
        print(f"   Calculated {measure_count} measures")
        
        return measures
    
    def create_materialized_views(self):
        """Create optimized views for faster dashboard queries"""
        print("\nCreating materialized views...")
        
        # View 1: Daily KPIs
        self.optimized_views['daily_kpis'] = self.orders.groupby('order_date').agg({
            'revenue': 'sum',
            'order_id': 'count',
            'customer_id': 'nunique',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        # View 2: Monthly KPIs
        self.optimized_views['monthly_kpis'] = self.orders.groupby(self.orders['order_date'].dt.to_period('M')).agg({
            'revenue': 'sum',
            'order_id': 'count',
            'profit': 'sum'
        }).reset_index()
        
        # View 3: Customer segment performance
        orders_with_seg = self.orders.merge(self.customers[['customer_id', 'segment', 'region']], on='customer_id')
        self.optimized_views['segment_performance'] = orders_with_seg.groupby(['segment', 'region']).agg({
            'revenue': 'sum',
            'customer_id': 'nunique',
            'order_id': 'count'
        }).reset_index()
        
        # View 4: Product category performance
        orders_with_cat = self.orders.merge(self.products[['product_id', 'category', 'subcategory']], on='product_id')
        self.optimized_views['category_performance'] = orders_with_cat.groupby(['category', 'subcategory']).agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        # View 5: Hourly trends
        self.optimized_views['hourly_trends'] = self.orders.groupby('hour').agg({
            'revenue': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        # Save views to CSV for dashboard
        for name, df in self.optimized_views.items():
            df.to_csv(f'data/{name}.csv', index=False)
        
        print(f"   Created {len(self.optimized_views)} materialized views")
    
    def save_to_database(self):
        """Save all processed data to SQLite - FIXED VERSION"""
        conn = sqlite3.connect(os.path.join(self.data_path, 'analytics.db'))
        
        # Save fact and dimension tables
        self.fact_orders.to_sql('fact_orders', conn, if_exists='replace', index=False)
        self.dim_customer.to_sql('dim_customer', conn, if_exists='replace', index=False)
        self.dim_product.to_sql('dim_product', conn, if_exists='replace', index=False)
        self.dim_date.to_sql('dim_date', conn, if_exists='replace', index=False)
        
        # Save metrics - FIXED: Convert everything to simple types
        metrics_list = []
        for k, v in self.results.items():
            # Skip complex types that cause SQLite errors
            if isinstance(v, (dict, list, pd.Series, pd.DataFrame)):
                continue
            # Convert to appropriate type
            if isinstance(v, (int, float, str, bool)):
                metrics_list.append({'metric_name': k, 'metric_value': v})
            else:
                # Convert anything else to string
                metrics_list.append({'metric_name': k, 'metric_value': str(v)})
        
        if metrics_list:
            metrics_df = pd.DataFrame(metrics_list)
            metrics_df.to_sql('metrics', conn, if_exists='replace', index=False)
            print(f"   Saved {len(metrics_list)} metrics to database")
        else:
            print("   No metrics to save")
        
        # Save materialized views
        for name, df in self.optimized_views.items():
            df.to_sql(name, conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"\nDatabase saved to {self.data_path}analytics.db")
    
    def run_complete_pipeline(self):
        """Execute all pipeline steps"""
        print("="*60)
        print("BI PIPELINE EXECUTION")
        print("="*60)
        
        start_time = time.time()
        
        self.load_data()
        self.create_star_schema()
        measures = self.calculate_all_measures()
        self.create_materialized_views()
        self.save_to_database()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE")
        print("="*60)
        print(f"Total duration: {duration:.2f} seconds")
        print(f"Total measures: {len(measures)}")
        print(f"Total tables: {len(self.optimized_views) + 4}")
        print("="*60)
        
        return measures

if __name__ == "__main__":
    pipeline = BIPipeline()
    results = pipeline.run_complete_pipeline()
    
    print("\nKEY METRICS:")
    print(f"   Total Revenue: ${results.get('total_revenue', 0):,.2f}")
    print(f"   Total Orders: {results.get('total_orders', 0):,}")
    print(f"   Profit Margin: {results.get('profit_margin', 0):.1f}%")
    print(f"   Repeat Purchase Rate: {results.get('repeat_purchase_rate', 0):.1f}%")
    print(f"   Customer LTV: ${results.get('customer_lifetime_value', 0):.2f}")
    print(f"   Return Rate: {results.get('return_rate', 0):.1f}%")
    print(f"   Marketing ROI: {results.get('marketing_roi', 0):.1f}%")
