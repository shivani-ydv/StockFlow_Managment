-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 01_schema.sql
-- Description: DDL definitions for tables, primary keys, foreign keys, 
--              unique constraints, check constraints, and performance indexes.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

DROP DATABASE IF EXISTS stockflow_db;
CREATE DATABASE stockflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stockflow_db;

-- ----------------------------------------------------------------------------
-- Table 1: CATEGORIES
-- Purpose: Classifies products into logical groups for inventory segmentation.
-- ----------------------------------------------------------------------------
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 2: SUPPLIERS
-- Purpose: Details of external vendors supplying products.
-- ----------------------------------------------------------------------------
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address TEXT,
    city VARCHAR(80),
    country VARCHAR(80) DEFAULT 'India',
    rating DECIMAL(2,1) DEFAULT 5.0 CHECK (rating >= 1.0 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 3: PRODUCTS
-- Purpose: Master catalog of all items sold or held in inventory.
-- Demonstrates: Foreign keys, UNIQUE SKU constraint, CHECK constraint.
-- ----------------------------------------------------------------------------
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    barcode VARCHAR(100) UNIQUE,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL CHECK (cost_price >= 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= cost_price),
    reorder_level INT NOT NULL DEFAULT 15 CHECK (reorder_level >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) 
        REFERENCES categories(category_id) ON DELETE RESTRICT,
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) 
        REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 4: WAREHOUSES
-- Purpose: Physical storage locations.
-- ----------------------------------------------------------------------------
CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_code VARCHAR(30) NOT NULL UNIQUE,
    warehouse_name VARCHAR(100) NOT NULL,
    location_city VARCHAR(80) NOT NULL,
    capacity_sqft INT NOT NULL CHECK (capacity_sqft > 0),
    manager_name VARCHAR(100),
    contact_phone VARCHAR(20),
    is_operational BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 5: INVENTORY
-- Purpose: Junction table tracking stock quantity of each product per warehouse.
-- Demonstrates: Composite uniqueness, Foreign keys, Non-negative stock CHECK constraint.
-- ----------------------------------------------------------------------------
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
    bin_location VARCHAR(30) DEFAULT 'A-01',
    last_restocked_at TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_warehouse UNIQUE (product_id, warehouse_id),
    CONSTRAINT fk_inventory_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_inventory_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 6: CUSTOMERS
-- Purpose: Buyers who place orders.
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    shipping_address TEXT NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80),
    pincode VARCHAR(20) NOT NULL,
    customer_type ENUM('Retail', 'Wholesale', 'Corporate') DEFAULT 'Retail',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 7: ORDERS
-- Purpose: Header table for customer purchase orders.
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0),
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    payment_status ENUM('Unpaid', 'Paid', 'Refunded') DEFAULT 'Unpaid',
    notes TEXT,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 8: ORDER_ITEMS
-- Purpose: Line items for each order specifying product, warehouse fulfilled from, quantity.
-- Demonstrates: Weak entity relationship to orders, calculations.
-- ----------------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price > 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal > 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_items_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 9: SHIPMENTS
-- Purpose: Fulfillment and dispatch tracking.
-- ----------------------------------------------------------------------------
CREATE TABLE shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    warehouse_id INT NOT NULL,
    carrier VARCHAR(80) NOT NULL,
    tracking_number VARCHAR(100) NOT NULL UNIQUE,
    shipping_status ENUM('Preparing', 'Dispatched', 'In Transit', 'Out for Delivery', 'Delivered', 'Failed') DEFAULT 'Preparing',
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    CONSTRAINT fk_shipments_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_shipments_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 10: STOCK_TRANSFERS
-- Purpose: Inter-warehouse inventory rebalancing.
-- ----------------------------------------------------------------------------
CREATE TABLE stock_transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    source_warehouse_id INT NOT NULL,
    destination_warehouse_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    status ENUM('Requested', 'In Transit', 'Completed', 'Cancelled') DEFAULT 'Requested',
    initiated_by VARCHAR(100) DEFAULT 'System Admin',
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    CONSTRAINT fk_transfer_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_transfer_src_wh FOREIGN KEY (source_warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    CONSTRAINT fk_transfer_dst_wh FOREIGN KEY (destination_warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    CONSTRAINT chk_diff_warehouses CHECK (source_warehouse_id <> destination_warehouse_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 11: INVENTORY_AUDIT_LOG
-- Purpose: Immutable record of inventory movements, price adjustments, and reconciliations.
-- ----------------------------------------------------------------------------
CREATE TABLE inventory_audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    change_type ENUM('ORDER_DEDUCT', 'RESTOCK', 'TRANSFER_OUT', 'TRANSFER_IN', 'MANUAL_ADJUSTMENT') NOT NULL,
    old_quantity INT NOT NULL,
    new_quantity INT NOT NULL,
    change_amount INT NOT NULL,
    reference_id VARCHAR(50),
    changed_by VARCHAR(80) DEFAULT 'SYSTEM',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_audit_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 12: INVENTORY_LEDGER (Event Movement Ledger)
-- Purpose: Double-entry movement log (+Restock, -Sale, -Damage, +Return).
-- Demonstrates: Event Sourcing, race condition prevention, true calculated stock.
-- ----------------------------------------------------------------------------
CREATE TABLE inventory_ledger (
    ledger_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    movement_type ENUM('INITIAL_COUNT', 'RESTOCK', 'SALE', 'DAMAGE', 'RETURN', 'TRANSFER_IN', 'TRANSFER_OUT', 'CSV_IMPORT', 'BARCODE_SCAN') NOT NULL,
    delta_quantity INT NOT NULL,
    balance_after INT NOT NULL,
    reference_type VARCHAR(50) DEFAULT 'MANUAL',
    reference_id VARCHAR(80),
    notes TEXT,
    recorded_by VARCHAR(80) DEFAULT 'SYSTEM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ledger_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_ledger_warehouse FOREIGN KEY (warehouse_id) 
        REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================================
-- PERFORMANCE INDEXES (Demonstrates B-Tree indexing for query optimization)
-- ============================================================================

-- Index for searching orders by customer and date range (Composite Index)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Index for finding order items by product
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Index on inventory lookups
CREATE INDEX idx_inventory_lookup ON inventory(product_id, warehouse_id);

-- Index on product categories for fast filtering
CREATE INDEX idx_products_category ON products(category_id);

-- Index on shipment tracking
CREATE INDEX idx_shipments_tracking ON shipments(tracking_number);
