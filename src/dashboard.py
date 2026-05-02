# src/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Enterprise BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load all data sources"""
    data = {}
    
    # Load fact and dimension tables if they exist
    if os.path.exists('data/fact_orders.csv'):
        data['fact_orders'] = pd.read_csv('data/fact_orders.csv')
        data['dim_customer'] = pd.read_csv('data/dim_customer.csv')
        data['dim_product'] = pd.read_csv('data/dim_product.csv')
        data['dim_date'] = pd.read_csv('data/dim_date.csv')
    else:
        # Fallback to raw data
        data['fact_orders'] = pd.read_csv('data/orders.csv')
        data['dim_customer'] = pd.read_csv('data/customers.csv')
        data['dim_product'] = pd.read_csv('data/products.csv')
    
    # Load materialized views
    view_files = ['daily_kpis.csv', 'monthly_kpis.csv', 'segment_performance.csv', 
                  'category_performance.csv', 'hourly_trends.csv']
    
    for view in view_files:
        path = f'data/{view}'
        if os.path.exists(path):
            data[view.replace('.csv', '')] = pd.read_csv(path)
    
    # Convert dates
    if 'fact_orders' in data:
        data['fact_orders']['order_date'] = pd.to_datetime(data['fact_orders']['order_date'])
    
    return data

def create_kpi_row(data):
    """Display KPI metrics at the top"""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Calculate KPIs
    total_revenue = data['fact_orders']['revenue'].sum()
    total_orders = len(data['fact_orders'])
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    unique_customers = data['fact_orders']['customer_id'].nunique()
    total_profit = data['fact_orders']['profit'].sum() if 'profit' in data['fact_orders'].columns else 0
    profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Total Orders", f"{total_orders:,}")
    with col3:
        st.metric("Avg Order Value", f"${avg_order:.2f}")
    with col4:
        st.metric("Unique Customers", f"{unique_customers:,}")
    with col5:
        st.metric("Total Profit", f"${total_profit:,.0f}")
    with col6:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")

def create_revenue_chart(data):
    """Revenue trend over time"""
    st.markdown('<div class="sub-header">Revenue Trend</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily revenue
        daily = data['fact_orders'].groupby('order_date')['revenue'].sum().reset_index()
        fig = px.line(daily, x='order_date', y='revenue', 
                      title="Daily Revenue",
                      labels={'order_date': 'Date', 'revenue': 'Revenue ($)'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly revenue
        data['fact_orders']['month'] = pd.to_datetime(data['fact_orders']['order_date']).dt.strftime('%Y-%m')
        monthly = data['fact_orders'].groupby('month')['revenue'].sum().reset_index()
        fig = px.bar(monthly, x='month', y='revenue',
                     title="Monthly Revenue",
                     labels={'month': 'Month', 'revenue': 'Revenue ($)'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def create_segmentation_charts(data):
    """Customer segmentation analysis"""
    st.markdown('<div class="sub-header">Customer Segmentation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by segment
        orders_with_seg = data['fact_orders'].merge(
            data['dim_customer'][['customer_id', 'segment']], 
            on='customer_id'
        )
        segment_revenue = orders_with_seg.groupby('segment')['revenue'].sum().reset_index()
        
        fig = px.pie(segment_revenue, values='revenue', names='segment',
                     title="Revenue by Customer Segment",
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by region
        region_revenue = orders_with_seg.groupby('region')['revenue'].sum().reset_index()
        
        fig = px.bar(region_revenue, x='region', y='revenue',
                     title="Revenue by Region",
                     labels={'region': 'Region', 'revenue': 'Revenue ($)'},
                     color='revenue')
        st.plotly_chart(fig, use_container_width=True)

def create_product_analysis(data):
    """Product performance analysis"""
    st.markdown('<div class="sub-header">Product Performance</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by category
        orders_with_cat = data['fact_orders'].merge(
            data['dim_product'][['product_id', 'category']], 
            on='product_id'
        )
        category_revenue = orders_with_cat.groupby('category')['revenue'].sum().reset_index()
        
        fig = px.bar(category_revenue, x='category', y='revenue',
                     title="Revenue by Category",
                     labels={'category': 'Category', 'revenue': 'Revenue ($)'},
                     color='revenue')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 products
        product_revenue = data['fact_orders'].merge(
            data['dim_product'][['product_id', 'product_name']], 
            on='product_id'
        )
        top_products = product_revenue.groupby('product_name')['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(top_products, x='product_name', y='revenue',
                     title="Top 10 Products",
                     labels={'product_name': 'Product', 'revenue': 'Revenue ($)'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def create_time_analysis(data):
    """Time-based analysis (hourly, weekly, monthly)"""
    st.markdown('<div class="sub-header">Time Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly trends
        if 'hourly_trends' in data:
            fig = px.bar(data['hourly_trends'], x='hour', y='order_id',
                         title="Orders by Hour of Day",
                         labels={'hour': 'Hour (0-23)', 'order_id': 'Number of Orders'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Weekend vs Weekday
        data['fact_orders']['day_type'] = data['fact_orders']['order_date'].dt.dayofweek.apply(
            lambda x: 'Weekend' if x >= 5 else 'Weekday'
        )
        day_type_revenue = data['fact_orders'].groupby('day_type')['revenue'].sum().reset_index()
        
        fig = px.pie(day_type_revenue, values='revenue', names='day_type',
                     title="Weekend vs Weekday Revenue",
                     hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

def create_monthly_table(data):
    """Monthly summary table"""
    st.markdown('<div class="sub-header">Monthly Performance Summary</div>', unsafe_allow_html=True)
    
    data['fact_orders']['year_month'] = pd.to_datetime(data['fact_orders']['order_date']).dt.strftime('%Y-%m')
    
    monthly_summary = data['fact_orders'].groupby('year_month').agg({
        'revenue': 'sum',
        'order_id': 'count',
        'customer_id': 'nunique',
        'profit': 'sum' if 'profit' in data['fact_orders'].columns else 'count'
    }).round(2).reset_index()
    
    monthly_summary.columns = ['Month', 'Revenue', 'Orders', 'Unique Customers', 'Profit']
    monthly_summary['Revenue'] = monthly_summary['Revenue'].apply(lambda x: f"${x:,.0f}")
    monthly_summary['Profit'] = monthly_summary['Profit'].apply(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else "N/A")
    
    st.dataframe(monthly_summary, use_container_width=True)

def main():
    """Main dashboard function"""
    st.markdown('<div class="main-header">Enterprise Business Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Complete analytics pipeline with 6 data sources, star schema, and 35+ business measures")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")
        
        # Date range filter
        if 'fact_orders' in data and not data['fact_orders'].empty:
            min_date = data['fact_orders']['order_date'].min()
            max_date = data['fact_orders']['order_date'].max()
            
            date_range = st.date_input(
                "Date Range",
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (data['fact_orders']['order_date'] >= pd.to_datetime(start_date)) & \
                       (data['fact_orders']['order_date'] <= pd.to_datetime(end_date))
                data['fact_orders'] = data['fact_orders'][mask]
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "This dashboard analyzes:\n"
            "- Revenue trends and profitability\n"
            "- Customer segments and behavior\n"
            "- Product category performance\n"
            "- Time-based patterns\n\n"
            "Built with Python, Pandas, Plotly, and Streamlit"
        )
    
    # Main dashboard content
    create_kpi_row(data)
    st.markdown("---")
    create_revenue_chart(data)
    st.markdown("---")
    create_segmentation_charts(data)
    st.markdown("---")
    create_product_analysis(data)
    st.markdown("---")
    create_time_analysis(data)
    st.markdown("---")
    create_monthly_table(data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: gray;'>"
        f"Data last processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Built with Streamlit"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
