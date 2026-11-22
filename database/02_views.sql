-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 02_views.sql
-- Description: Business reporting and security views demonstrating complex JOINs,
--              aggregations, and computed columns.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

USE stockflow_db;

-- ----------------------------------------------------------------------------
-- View 1: vw_low_stock_alerts
-- Purpose: Real-time alert feed for items where quantity is at or below reorder level.
-- Demonstrates: Multi-table INNER JOIN, WHERE filter, computed status flag.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_low_stock_alerts AS
SELECT 
    p.product_id,
    p.sku,
    p.product_name,
    c.category_name,
    w.warehouse_id,
    w.warehouse_name,
    w.location_city,
    i.quantity_on_hand,
    p.reorder_level,
    (p.reorder_level - i.quantity_on_hand) AS units_deficit,
    s.company_name AS supplier_name,
    s.contact_person AS supplier_contact,
    s.phone AS supplier_phone,
    CASE 
        WHEN i.quantity_on_hand = 0 THEN 'OUT_OF_STOCK'
        WHEN i.quantity_on_hand <= (p.reorder_level / 2) THEN 'CRITICAL'
        ELSE 'LOW_STOCK'
    END AS urgency_level
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE i.quantity_on_hand <= p.reorder_level
ORDER BY urgency_level DESC, units_deficit DESC;

-- ----------------------------------------------------------------------------
-- View 2: vw_inventory_valuation
-- Purpose: Financial executive report calculating inventory value at cost and retail.
-- Demonstrates: GROUP BY with multi-level grouping and SUM/AVG aggregations.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_inventory_valuation AS
SELECT 
    w.warehouse_name,
    w.location_city,
    c.category_name,
    COUNT(DISTINCT p.product_id) AS total_unique_products,
    SUM(i.quantity_on_hand) AS total_units_in_stock,
    ROUND(SUM(i.quantity_on_hand * p.cost_price), 2) AS total_inventory_cost,
    ROUND(SUM(i.quantity_on_hand * p.unit_price), 2) AS total_inventory_market_value,
    ROUND(SUM(i.quantity_on_hand * (p.unit_price - p.cost_price)), 2) AS projected_gross_profit
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name, w.location_city, c.category_name;

-- ----------------------------------------------------------------------------
-- View 3: vw_customer_order_summary
-- Purpose: Complete customer 360-view showing lifetime orders and spend.
-- Demonstrates: LEFT JOIN to include customers with zero orders, IFNULL, aggregates.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_customer_order_summary AS
SELECT 
    c.customer_id,
    c.full_name,
    c.email,
    c.customer_type,
    c.city,
    COUNT(o.order_id) AS total_orders_placed,
    IFNULL(SUM(CASE WHEN o.status <> 'Cancelled' THEN o.total_amount ELSE 0 END), 0.00) AS lifetime_spent,
    MAX(o.order_date) AS most_recent_order_date,
    CASE 
        WHEN SUM(o.total_amount) > 100000 THEN 'Platinum'
        WHEN SUM(o.total_amount) > 50000 THEN 'Gold'
        WHEN SUM(o.total_amount) > 10000 THEN 'Silver'
        ELSE 'Bronze'
    END AS customer_tier
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name, c.email, c.customer_type, c.city;

-- ----------------------------------------------------------------------------
-- View 4: vw_order_fulfillment_overview
-- Purpose: Consolidates order details, line count, dispatch warehouse, and shipment tracking.
-- Demonstrates: 4-table JOIN including optional 1:1 relationship with shipments.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_order_fulfillment_overview AS
SELECT 
    o.order_id,
    o.order_number,
    o.order_date,
    o.status AS order_status,
    o.total_amount,
    c.full_name AS customer_name,
    c.email AS customer_email,
    c.city AS shipping_city,
    COUNT(oi.order_item_id) AS total_distinct_items,
    SUM(oi.quantity) AS total_items_quantity,
    s.carrier,
    s.tracking_number,
    s.shipping_status,
    s.shipped_at
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN shipments s ON o.order_id = s.order_id
GROUP BY 
    o.order_id, o.order_number, o.order_date, o.status, o.total_amount,
    c.full_name, c.email, c.city, s.carrier, s.tracking_number, s.shipping_status, s.shipped_at;
