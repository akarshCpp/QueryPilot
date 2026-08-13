import json
import os
import subprocess
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment from .env file or default Supabase local DB URL
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

def insert_data(data):
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print("Inserting regions...")
        execute_values(cursor, "INSERT INTO regions (id, name) VALUES %s ON CONFLICT DO NOTHING", 
                       [(r['id'], r['name']) for r in data['regions']])

        print("Inserting categories...")
        execute_values(cursor, "INSERT INTO categories (id, name, description) VALUES %s ON CONFLICT DO NOTHING", 
                       [(c['id'], c['name'], c['description']) for c in data['categories']])

        print("Inserting products...")
        execute_values(cursor, "INSERT INTO products (id, category_id, name, description, price, cost) VALUES %s ON CONFLICT DO NOTHING", 
                       [(p['id'], p['category_id'], p['name'], p['description'], p['price'], p['cost']) for p in data['products']])

        print("Inserting customers...")
        execute_values(cursor, "INSERT INTO customers (id, name, email, segment, region_id) VALUES %s ON CONFLICT DO NOTHING", 
                       [(c['id'], c['name'], c['email'], c['segment'], c['region_id']) for c in data['customers']])

        print("Inserting orders...")
        execute_values(cursor, "INSERT INTO orders (id, customer_id, order_date, status) VALUES %s ON CONFLICT DO NOTHING", 
                       [(o['id'], o['customer_id'], o['order_date'], o['status']) for o in data['orders']])

        print("Inserting sales...")
        # total_amount is GENERATED ALWAYS, so omit it
        execute_values(cursor, "INSERT INTO sales (id, order_id, product_id, quantity, unit_price, discount) VALUES %s ON CONFLICT DO NOTHING", 
                       [(s['id'], s['order_id'], s['product_id'], s['quantity'], s['unit_price'], s['discount']) for s in data['sales']])

        print("Inserting returns...")
        execute_values(cursor, "INSERT INTO returns (id, sale_id, return_date, reason, refund_amount) VALUES %s ON CONFLICT DO NOTHING", 
                       [(r['id'], r['sale_id'], r['return_date'], r['reason'], r['refund_amount']) for r in data['returns']])

        # Update sequences so new inserts don't fail
        tables = ["regions", "categories", "products", "customers", "orders", "sales", "returns"]
        for table in tables:
            cursor.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM {table}));")

        print("Successfully seeded all tables.")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if not os.path.exists("data/ecommerce_seed.json"):
        print("Data file not found. Running generate_data.py...")
        subprocess.run(["python", "scripts/generate_data.py"])
        
    with open("data/ecommerce_seed.json", "r") as f:
        data = json.load(f)
        
    insert_data(data)
