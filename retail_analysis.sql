CREATE DATABASE IF NOT EXISTS retail_analysis;
USE retail_analysis;

-- Create this table only if you have not already imported the data.
CREATE TABLE IF NOT EXISTS superstore (
    row_id INT,
    order_id VARCHAR(30),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(30),
    customer_id VARCHAR(30),
    customer_name VARCHAR(100),
    segment VARCHAR(30),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(30),
    product_id VARCHAR(30),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    product_name VARCHAR(255),
    sales DECIMAL(15,2),
    sales_validated BOOLEAN DEFAULT FALSE
);

-- 1. Dataset overview
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products
FROM superstore;

-- 2. Check missing essential values
SELECT
    SUM(order_id IS NULL OR order_id = '') AS missing_order_ids,
    SUM(customer_id IS NULL OR customer_id = '') AS missing_customer_ids,
    SUM(product_id IS NULL OR product_id = '') AS missing_product_ids,
    SUM(order_date IS NULL) AS missing_order_dates,
    SUM(sales IS NULL) AS missing_sales
FROM superstore;

-- 3. Check potential duplicate records
SELECT
    row_id, order_id, order_date, ship_date, customer_id,
    product_id, product_name, COUNT(*) AS duplicate_count
FROM superstore
GROUP BY
    row_id, order_id, order_date, ship_date, customer_id,
    product_id, product_name
HAVING COUNT(*) > 1;

-- 4. Order activity by category
SELECT
    category,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT product_id) AS unique_products,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY category
ORDER BY total_orders DESC;

-- 5. Regional order performance
SELECT
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY region
ORDER BY total_orders DESC;

-- 6. Monthly order trends
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
WHERE order_date IS NOT NULL
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;

-- 7. Customer segment analysis
SELECT
    segment,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
GROUP BY segment
ORDER BY total_orders DESC;

-- 8. Top 10 products by order-line count (not by revenue)
SELECT
    product_id,
    product_name,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
GROUP BY product_id, product_name
ORDER BY order_lines DESC
LIMIT 10;

-- 9. Sales by category (run only after validating Sales values)
SELECT
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
WHERE sales_validated = TRUE
GROUP BY category
ORDER BY total_sales DESC;

-- 10. Sales by region (run only after validating Sales values)
SELECT
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
WHERE sales_validated = TRUE
GROUP BY region
ORDER BY total_sales DESC;

-- 11. Monthly sales trend (run only after validating Sales values)
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS order_month,
    ROUND(SUM(sales), 2) AS total_sales,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
WHERE order_date IS NOT NULL
  AND sales_validated = TRUE
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;

-- 12. Sales by customer segment (run only after validating Sales values)
SELECT
    segment,
    ROUND(SUM(sales), 2) AS total_sales,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
WHERE sales_validated = TRUE
GROUP BY segment
ORDER BY total_sales DESC;
USE retail_analysis;

-- Check total rows
SELECT COUNT(*) AS total_rows
FROM superstore;

-- Preview the data
SELECT *
FROM superstore
LIMIT 10;

-- Check available columns
DESCRIBE superstore;
SELECT
    category,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products
FROM superstore
GROUP BY category
ORDER BY total_orders DESC;
SELECT
    region,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY region
ORDER BY total_orders DESC;
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;
SELECT
    segment,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY segment
ORDER BY total_orders DESC;
SELECT
    product_name,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders
FROM superstore
GROUP BY product_name
ORDER BY total_orders DESC
LIMIT 10;
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;
SELECT
    region,
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM superstore
GROUP BY region
ORDER BY total_orders DESC;
-- End of script