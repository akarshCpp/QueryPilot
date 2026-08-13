# Database Schema and Relationships

## Tables

### 1. regions
Contains geographical regions.
- `id`: Primary key.
- `name`: Region name (e.g., North America, Europe).

### 2. categories
Contains product categories.
- `id`: Primary key.
- `name`: Category name (e.g., Electronics, Apparel).

### 3. products
Contains product details.
- `id`: Primary key.
- `category_id`: Foreign key to `categories.id`.
- `name`: Product name.
- `price`: Selling price per unit.
- `cost`: Cost to manufacture/procure per unit.

### 4. customers
Contains customer information.
- `id`: Primary key.
- `segment`: Customer classification (Retail, Wholesale, VIP).
- `region_id`: Foreign key to `regions.id`.

### 5. orders
Contains order headers.
- `id`: Primary key.
- `customer_id`: Foreign key to `customers.id`.
- `status`: Order status (Pending, Completed, Cancelled).

### 6. sales
Contains order line items (individual products sold in an order).
- `id`: Primary key.
- `order_id`: Foreign key to `orders.id`.
- `product_id`: Foreign key to `products.id`.
- `quantity`: Number of units sold.
- `unit_price`: Price per unit at time of sale.
- `discount`: Discount applied to this line item.
- `total_amount`: Pre-calculated as `(quantity * unit_price) - discount`.

### 7. returns
Contains records of returned items.
- `id`: Primary key.
- `sale_id`: Foreign key to `sales.id`.
- `refund_amount`: Amount refunded to the customer.

## Key Relationships for Joins
- To find regional sales: `sales` -> `orders` -> `customers` -> `regions`.
- To find category sales: `sales` -> `products` -> `categories`.
- To find returns by region: `returns` -> `sales` -> `orders` -> `customers` -> `regions`.
