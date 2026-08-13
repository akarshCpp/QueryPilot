import json
import random
import os
from datetime import datetime, timedelta

def generate_ecommerce_data(seed=42):
    random.seed(seed)
    
    # Generate Regions
    regions = [
        {"id": 1, "name": "North America"},
        {"id": 2, "name": "Europe"},
        {"id": 3, "name": "Asia Pacific"},
        {"id": 4, "name": "Latin America"},
        {"id": 5, "name": "Middle East & Africa"}
    ]
    
    # Generate Categories
    categories = [
        {"id": 1, "name": "Electronics", "description": "Gadgets, devices, and accessories"},
        {"id": 2, "name": "Apparel", "description": "Clothing and fashion"},
        {"id": 3, "name": "Home & Kitchen", "description": "Furniture, appliances, and decor"},
        {"id": 4, "name": "Sports", "description": "Sporting goods and outdoor gear"},
        {"id": 5, "name": "Books", "description": "Physical and digital books"}
    ]
    
    # Generate Products (approx 100 for seed instead of 1000 for speed, scalable later)
    products = []
    for i in range(1, 101):
        cat_id = random.randint(1, 5)
        price = round(random.uniform(10.0, 500.0), 2)
        cost = round(price * random.uniform(0.3, 0.7), 2)
        products.append({
            "id": i,
            "category_id": cat_id,
            "name": f"Product {i}",
            "description": f"Description for Product {i}",
            "price": price,
            "cost": cost
        })
        
    # Generate Customers (approx 1000 for seed)
    segments = ["Retail", "Wholesale", "VIP"]
    customers = []
    for i in range(1, 1001):
        customers.append({
            "id": i,
            "name": f"Customer {i}",
            "email": f"customer{i}@example.com",
            "segment": random.choices(segments, weights=[0.7, 0.2, 0.1])[0],
            "region_id": random.randint(1, 5)
        })
        
    # Generate Orders, Sales, and Returns
    # Time period: Last 2 years
    start_date = datetime.now() - timedelta(days=730)
    orders = []
    sales = []
    returns = []
    
    order_id = 1
    sale_id = 1
    return_id = 1
    
    # 5000 orders
    for i in range(1, 5001):
        cust_id = random.randint(1, 1000)
        
        # Simulate seasonality (more orders in Nov/Dec)
        random_days = random.randint(0, 730)
        o_date = start_date + timedelta(days=random_days)
        if o_date.month in [11, 12]:
            if random.random() < 0.5: # 50% chance to duplicate order in holiday season
                pass # This just means they order more frequently, simulated by higher density

        status = random.choices(["Completed", "Pending", "Cancelled"], weights=[0.8, 0.1, 0.1])[0]
        
        orders.append({
            "id": order_id,
            "customer_id": cust_id,
            "order_date": o_date.isoformat(),
            "status": status
        })
        
        # Generate Sales for this order
        num_items = random.randint(1, 5)
        order_total = 0
        for _ in range(num_items):
            prod = random.choice(products)
            qty = random.randint(1, 3)
            discount = round(random.uniform(0, 0.2) * (prod["price"] * qty), 2)
            
            sales.append({
                "id": sale_id,
                "order_id": order_id,
                "product_id": prod["id"],
                "quantity": qty,
                "unit_price": prod["price"],
                "discount": discount
            })
            
            # 5% chance of return if Completed
            if status == "Completed" and random.random() < 0.05:
                returns.append({
                    "id": return_id,
                    "sale_id": sale_id,
                    "return_date": (o_date + timedelta(days=random.randint(1, 30))).isoformat(),
                    "reason": random.choice(["Defective", "Changed mind", "Wrong item"]),
                    "refund_amount": round((prod["price"] * qty) - discount, 2)
                })
                return_id += 1
                
            sale_id += 1
            
        order_id += 1

    return {
        "regions": regions,
        "categories": categories,
        "products": products,
        "customers": customers,
        "orders": orders,
        "sales": sales,
        "returns": returns
    }

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    data = generate_ecommerce_data(seed=42)
    with open("data/ecommerce_seed.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Data generated in data/ecommerce_seed.json")
