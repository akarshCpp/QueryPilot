-- Performance and Vector Indexes

-- Foreign Key Indexes for E-Commerce Tables
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_customers_region ON customers(region_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_sales_order ON sales(order_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_returns_sale ON returns(sale_id);

-- Vector Index for similarity search
CREATE INDEX idx_knowledge_chunks_embedding 
ON knowledge_chunks 
USING hnsw (embedding vector_cosine_ops);

-- GIN Index for Metadata filtering
CREATE INDEX idx_knowledge_chunks_metadata ON knowledge_chunks USING GIN (metadata);

-- Full Text Search Index on knowledge chunks
ALTER TABLE knowledge_chunks ADD COLUMN fts tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_knowledge_chunks_fts ON knowledge_chunks USING GIN (fts);
