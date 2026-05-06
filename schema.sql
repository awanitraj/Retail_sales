CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(100)
);

CREATE TABLE dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    description TEXT,
    current_unit_price DECIMAL(10, 2)
);

CREATE TABLE sales_fact (
    transaction_id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50),
    customer_id VARCHAR(50) REFERENCES dim_customer (customer_id),
    product_id VARCHAR(50) REFERENCES dim_product (product_id),
    invoice_date TIMESTAMP,
    quantity INT,
    total_amount DECIMAL(10, 2)
);

CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT
    DATE(invoice_date) as sales_date,
    SUM(total_amount) as daily_revenue,
    COUNT(DISTINCT invoice_no) as total_orders
FROM sales_fact
GROUP BY
    DATE(invoice_date)
ORDER BY sales_date;


CREATE OR REPLACE VIEW vw_customer_segments AS
WITH
    customer_aggregates AS (
        SELECT
            customer_id,
            MAX(invoice_date) as last_purchase_date,
            COUNT(DISTINCT invoice_no) as frequency,
            SUM(total_amount) as monetary
        FROM sales_fact
        GROUP BY
            customer_id
    ),
    rfm_calculations AS (
        SELECT
            customer_id,
            frequency,
            monetary,
            (
                SELECT MAX(invoice_date)
                FROM sales_fact
            ) - last_purchase_date AS recency_interval
        FROM customer_aggregates
    )
SELECT
    customer_id,
    frequency,
    monetary,
    CASE
        WHEN monetary > 2500 THEN 'High Value'
        WHEN frequency >= 10 THEN 'Frequent Buyer'
        WHEN frequency <= 3 THEN 'Occasional Customer'
        ELSE 'Standard Customer'
    END as segment
FROM rfm_calculations;