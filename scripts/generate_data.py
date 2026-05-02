# scripts/generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_all_data():
    """Generate 6 data sources: orders, customers, products, marketing, inventory, returns"""
    
    os.makedirs('data', exist_ok=True)
    
    print("="*60)
    print("DATA GENERATION - 6 SOURCES")
    print("="*60)
    
    np.random.seed(42)
    random.seed(42)
    
    # Date range: 2 years of data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(current)
        current = current + timedelta(days=1)
    
    # ============================================
    # SOURCE 1: CUSTOMERS (5,000 customers)
    # ============================================
    print("\n[1/6] Generating customers...")
    
    segments = ['Premium', 'Gold', 'Silver', 'Bronze']
    segment_weights = [0.15, 0.25, 0.35, 0.25]
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    customers = []
    for i in range(1, 5001):
        customer = {
            'customer_id': i,
            'customer_name': f'Customer_{i}',
            'segment': np.random.choice(segments, p=segment_weights),
            'region': np.random.choice(regions),
            'signup_date': np.random.choice(date_list[:365]),
            'email': f'customer{i}@example.com'
        }
        customers.append(customer)
    
    customers_df = pd.DataFrame(customers)
    customers_df.to_csv('data/customers.csv', index=False)
    print(f"   Created {len(customers_df):,} customers")
    
    # ============================================
    # SOURCE 2: PRODUCTS (200 products)
    # ============================================
    print("\n[2/6] Generating products...")
    
    categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books']
    subcategories = {
        'Electronics': ['Laptops', 'Phones', 'Tablets', 'Accessories'],
        'Clothing': ['Men', 'Women', 'Kids', 'Accessories'],
        'Home': ['Furniture', 'Decor', 'Kitchen', 'Bedding'],
        'Sports': ['Equipment', 'Apparel', 'Footwear', 'Accessories'],
        'Books': ['Fiction', 'Non-Fiction', 'Textbooks', 'Children']
    }
    
    products = []
    for i in range(1, 201):
        category = np.random.choice(categories)
        subcategory = np.random.choice(subcategories[category])
        cost = np.random.uniform(5, 200)
        
        product = {
            'product_id': i,
            'product_name': f'Product_{i}',
            'category': category,
            'subcategory': subcategory,
            'cost_price': round(cost, 2),
            'selling_price': round(cost * np.random.uniform(1.3, 2.5), 2),
            'weight_kg': round(np.random.uniform(0.1, 5.0), 2)
        }
        products.append(product)
    
    products_df = pd.DataFrame(products)
    products_df.to_csv('data/products.csv', index=False)
    print(f"   Created {len(products_df)} products across {len(categories)} categories")
    
    # ============================================
    # SOURCE 3: ORDERS (50,000 orders)
    # ============================================
    print("\n[3/6] Generating orders...")
    
    orders = []
    for i in range(1, 50001):
        customer_id = np.random.randint(1, 5001)
        product_id = np.random.randint(1, 201)
        product = products_df[products_df['product_id'] == product_id].iloc[0]
        
        quantity = np.random.randint(1, 6)
        revenue = round(product['selling_price'] * quantity, 2)
        cost = round(product['cost_price'] * quantity, 2)
        profit = round(revenue - cost, 2)
        
        order_date = np.random.choice(date_list)
        
        # Add timestamp for hourly analysis
        hour = np.random.randint(0, 24)
        order_timestamp = datetime.combine(order_date.date(), datetime.min.time()) + timedelta(hours=hour)
        
        order = {
            'order_id': i,
            'order_date': order_date,
            'order_timestamp': order_timestamp,
            'customer_id': customer_id,
            'product_id': product_id,
            'quantity': quantity,
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'discount': round(revenue * np.random.uniform(0, 0.2), 2) if np.random.random() < 0.3 else 0
        }
        orders.append(order)
    
    orders_df = pd.DataFrame(orders)
    orders_df.to_csv('data/orders.csv', index=False)
    print(f"   Created {len(orders_df):,} orders")
    print(f"   Total revenue: ${orders_df['revenue'].sum():,.2f}")
    
    # ============================================
    # SOURCE 4: MARKETING (daily by channel)
    # ============================================
    print("\n[4/6] Generating marketing data...")
    
    channels = ['Google', 'Facebook', 'Instagram', 'Email', 'TV']
    marketing = []
    
    for date in date_list:
        for channel in channels:
            spend = np.random.uniform(100, 5000)
            impressions = int(np.random.uniform(10000, 500000))
            clicks = int(impressions * np.random.uniform(0.01, 0.05))
            
            marketing.append({
                'date': date,
                'channel': channel,
                'spend': round(spend, 2),
                'impressions': impressions,
                'clicks': clicks,
                'conversions': int(clicks * np.random.uniform(0.05, 0.15))
            })
    
    marketing_df = pd.DataFrame(marketing)
    marketing_df.to_csv('data/marketing.csv', index=False)
    print(f"   Created {len(marketing_df):,} marketing records")
    print(f"   Total marketing spend: ${marketing_df['spend'].sum():,.2f}")
    
    # ============================================
    # SOURCE 5: INVENTORY (daily stock levels)
    # ============================================
    print("\n[5/6] Generating inventory data...")
    
    inventory = []
    # Sample every 7 days instead of daily to keep size reasonable
    sample_dates = date_list[::7]
    
    for date in sample_dates:
        for product_id in range(1, 201):
            base_stock = np.random.randint(50, 500)
            # Add seasonal variation
            month = date.month
            if month in [11, 12]:  # Holiday season
                multiplier = 0.5
            elif month in [1, 2]:  # Post-holiday
                multiplier = 1.5
            else:
                multiplier = 1.0
            
            stock = int(base_stock * multiplier)
            
            inventory.append({
                'date': date,
                'product_id': product_id,
                'stock_level': max(0, stock + np.random.randint(-50, 50)),
                'reorder_point': 50,
                'safety_stock': 25
            })
    
    inventory_df = pd.DataFrame(inventory)
    inventory_df.to_csv('data/inventory.csv', index=False)
    print(f"   Created {len(inventory_df):,} inventory records")
    
    # ============================================
    # SOURCE 6: RETURNS (~5% of orders)
    # ============================================
    print("\n[6/6] Generating returns data...")
    
    # Select ~5% of orders as returned
    return_orders = np.random.choice(orders_df['order_id'], 
                                      size=int(len(orders_df) * 0.05), 
                                      replace=False)
    
    reasons = ['defective', 'wrong_item', 'damaged_shipping', 'not_wanted', 'size_issue']
    
    returns = []
    for idx, order_id in enumerate(return_orders[:5000], 1):  # Limit to 5000 returns
        original_order = orders_df[orders_df['order_id'] == order_id].iloc[0]
        
        # Return usually happens within 30 days of purchase
        return_days = np.random.randint(1, 30)
        return_date = original_order['order_date'] + timedelta(days=return_days)
        
        if return_date <= end_date:
            returns.append({
                'return_id': idx,
                'order_id': order_id,
                'return_date': return_date,
                'reason': np.random.choice(reasons),
                'refund_amount': original_order['revenue'],
                'restocking_fee': round(original_order['revenue'] * np.random.uniform(0, 0.15), 2)
            })
    
    returns_df = pd.DataFrame(returns)
    returns_df.to_csv('data/returns.csv', index=False)
    print(f"   Created {len(returns_df):,} returns records")
    print(f"   Return rate: {(len(returns_df) / len(orders_df)) * 100:.1f}%")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "="*60)
    print("DATA GENERATION COMPLETE")
    print("="*60)
    print("\nData sources created:")
    print(f"   1. Customers:   {len(customers_df):,} records")
    print(f"   2. Products:    {len(products_df)} records")
    print(f"   3. Orders:      {len(orders_df):,} records")
    print(f"   4. Marketing:   {len(marketing_df):,} records")
    print(f"   5. Inventory:   {len(inventory_df):,} records")
    print(f"   6. Returns:     {len(returns_df):,} records")
    print("\nFiles saved in 'data/' folder:")
    print("   - customers.csv")
    print("   - products.csv")
    print("   - orders.csv")
    print("   - marketing.csv")
    print("   - inventory.csv")
    print("   - returns.csv")
    print("="*60)

if __name__ == "__main__":
    generate_all_data()
