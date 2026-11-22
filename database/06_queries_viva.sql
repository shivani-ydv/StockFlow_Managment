-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 06_queries_viva.sql
-- Description: Comprehensive suite of 16 exam & viva SQL queries covering
--              joins, subqueries, group by, having, window functions, and EXPLAIN.
-- ============================================================================

USE stockflow_db;

-- ----------------------------------------------------------------------------
-- Q1: Multi-Table INNER JOIN (4 Tables)
-- Concept: Retrieve detailed line items with customer name, product, and warehouse.
-- ----------------------------------------------------------------------------
SELECT 
    o.order_number,
    c.full_name AS customer,
    p.product_name,
    w.warehouse_name,
    oi.quantity,
    oi.unit_price,
    oi.subtotal
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN warehouses w ON oi.warehouse_id = w.warehouse_id
ORDER BY o.order_date DESC;

-- ----------------------------------------------------------------------------
-- Q2: LEFT OUTER JOIN
-- Concept: Find products that have NEVER been ordered by any customer.
-- ----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.sku,
    p.product_name,
    c.category_name,
    p.unit_price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
JOIN categories c ON p.category_id = c.category_id
WHERE oi.order_item_id IS NULL;

-- ----------------------------------------------------------------------------
-- Q3: Self-Join
-- Concept: Compare warehouses in different cities that hold the SAME product.
-- ----------------------------------------------------------------------------
SELECT 
    p.product_name,
    w1.warehouse_name AS warehouse_a,
    i1.quantity_on_hand AS stock_a,
    w2.warehouse_name AS warehouse_b,
    i2.quantity_on_hand AS stock_b
FROM inventory i1
JOIN inventory i2 ON i1.product_id = i2.product_id AND i1.warehouse_id < i2.warehouse_id
JOIN products p ON i1.product_id = p.product_id
JOIN warehouses w1 ON i1.warehouse_id = w1.warehouse_id
JOIN warehouses w2 ON i2.warehouse_id = w2.warehouse_id
WHERE i1.quantity_on_hand > 0 AND i2.quantity_on_hand > 0;

-- ----------------------------------------------------------------------------
-- Q4: GROUP BY with HAVING Clause
-- Concept: Find suppliers whose catalog products average unit price exceeds 20,000 INR.
-- ----------------------------------------------------------------------------
SELECT 
    s.supplier_id,
    s.company_name,
    s.city,
    COUNT(p.product_id) AS total_products_supplied,
    ROUND(AVG(p.unit_price), 2) AS avg_product_price,
    ROUND(MAX(p.unit_price), 2) AS highest_priced_item
FROM suppliers s
JOIN products p ON s.supplier_id = p.supplier_id
GROUP BY s.supplier_id, s.company_name, s.city
HAVING AVG(p.unit_price) > 20000.00
ORDER BY avg_product_price DESC;

-- ----------------------------------------------------------------------------
-- Q5: Non-Correlated Subquery (IN)
-- Concept: Find all customers who have placed orders with a total amount > 75,000 INR.
-- ----------------------------------------------------------------------------
SELECT 
    customer_id,
    full_name,
    email,
    city
FROM customers
WHERE customer_id IN (
    SELECT customer_id 
    FROM orders 
    WHERE total_amount > 75000.00
);

-- ----------------------------------------------------------------------------
-- Q6: Correlated Subquery
-- Concept: Find products whose unit price is GREATER than the average unit price
--          of ALL products in that same category! (A favourite viva question!)
-- ----------------------------------------------------------------------------
SELECT 
    p1.product_id,
    p1.sku,
    p1.product_name,
    p1.category_id,
    p1.unit_price
FROM products p1
WHERE p1.unit_price > (
    SELECT AVG(p2.unit_price)
    FROM products p2
    WHERE p2.category_id = p1.category_id
);

-- ----------------------------------------------------------------------------
-- Q7: Correlated Subquery with EXISTS
-- Concept: Find warehouses that currently store AT LEAST ONE out-of-stock product.
-- ----------------------------------------------------------------------------
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.location_city
FROM warehouses w
WHERE EXISTS (
    SELECT 1 
    FROM inventory i 
    WHERE i.warehouse_id = w.warehouse_id AND i.quantity_on_hand = 0
);

-- ----------------------------------------------------------------------------
-- Q8: Window Function: DENSE_RANK()
-- Concept: Rank top 3 most expensive products within EACH category.
-- ----------------------------------------------------------------------------
SELECT 
    category_name,
    product_name,
    unit_price,
    price_rank_in_category
FROM (
    SELECT 
        c.category_name,
        p.product_name,
        p.unit_price,
        DENSE_RANK() OVER (PARTITION BY p.category_id ORDER BY p.unit_price DESC) AS price_rank_in_category
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
) ranked
WHERE price_rank_in_category <= 3;

-- ----------------------------------------------------------------------------
-- Q9: Window Function: Cumulative Running Total
-- Concept: Calculate running total of order revenue sorted by order date.
-- ----------------------------------------------------------------------------
SELECT 
    order_id,
    order_number,
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_revenue
FROM orders
WHERE status <> 'Cancelled';

-- ----------------------------------------------------------------------------
-- Q10: Set Operation: UNION ALL
-- Concept: Unified inventory movement feed from shipments and inter-warehouse transfers.
-- ----------------------------------------------------------------------------
SELECT 
    'CUSTOMER_SHIPMENT' AS movement_type,
    s.tracking_number AS reference,
    w.warehouse_name,
    s.shipped_at AS activity_timestamp
FROM shipments s
JOIN warehouses w ON s.warehouse_id = w.warehouse_id
WHERE s.shipped_at IS NOT NULL

UNION ALL

SELECT 
    'WAREHOUSE_TRANSFER' AS movement_type,
    CONCAT('TRF-', t.transfer_id) AS reference,
    w.warehouse_name,
    t.initiated_at AS activity_timestamp
FROM stock_transfers t
JOIN warehouses w ON t.source_warehouse_id = w.warehouse_id
ORDER BY activity_timestamp DESC;

-- ----------------------------------------------------------------------------
-- Q11: Performance & EXPLAIN Plan Analysis
-- Concept: Compare query execution cost with and without index utilization.
-- ----------------------------------------------------------------------------
EXPLAIN ANALYZE 
SELECT o.order_number, c.full_name, o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.customer_id = 2 AND o.order_date >= '2026-11-01';

-- ----------------------------------------------------------------------------
-- Q12: Query Views Directly
-- ----------------------------------------------------------------------------
SELECT * FROM vw_low_stock_alerts;
SELECT * FROM vw_inventory_valuation;
SELECT * FROM vw_customer_order_summary ORDER BY lifetime_spent DESC;
