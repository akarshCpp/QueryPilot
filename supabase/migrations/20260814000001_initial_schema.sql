-- Initial Schema for QueryPilot E-commerce Analytics

CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    segment VARCHAR(50) NOT NULL, -- e.g., 'Retail', 'Wholesale', 'VIP'
    region_id INTEGER REFERENCES regions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL -- e.g., 'Completed', 'Cancelled', 'Pending'
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(10, 2) GENERATED ALWAYS AS ((quantity * unit_price) - discount) STORED
);

CREATE TABLE returns (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id),
    return_date TIMESTAMP WITH TIME ZONE NOT NULL,
    reason TEXT,
    refund_amount DECIMAL(10, 2) NOT NULL
);
