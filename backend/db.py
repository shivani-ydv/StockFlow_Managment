"""
StockFlow Database Manager & Schema Initializer
Supports SQLite out of the box with strict relational constraints,
views, triggers, and transactions enabled.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "stockflow.db")

def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite database with Foreign Keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Crucial for DBMS projects: Turn on Foreign Key enforcement in SQLite!
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database() -> None:
    """Initializes the database schema, views, triggers, and sample data."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.executescript("""
    -- 1. Categories
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 2. Suppliers
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_person TEXT,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        address TEXT,
        city TEXT,
        country TEXT DEFAULT 'India',
        rating REAL DEFAULT 5.0 CHECK (rating >= 1.0 AND rating <= 5.0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 3. Products
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL UNIQUE,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        supplier_id INTEGER NOT NULL,
        cost_price REAL NOT NULL CHECK (cost_price >= 0),
        unit_price REAL NOT NULL CHECK (unit_price >= cost_price),
        reorder_level INTEGER NOT NULL DEFAULT 15 CHECK (reorder_level >= 0),
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
    );

    -- 4. Warehouses
    CREATE TABLE IF NOT EXISTS warehouses (
        warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_code TEXT NOT NULL UNIQUE,
        warehouse_name TEXT NOT NULL,
        location_city TEXT NOT NULL,
        capacity_sqft INTEGER NOT NULL CHECK (capacity_sqft > 0),
        manager_name TEXT,
        contact_phone TEXT,
        is_operational INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 5. Inventory
    CREATE TABLE IF NOT EXISTS inventory (
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        quantity_on_hand INTEGER NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
        bin_location TEXT DEFAULT 'A-01',
        last_restocked_at TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (product_id, warehouse_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
    );

    -- 6. Customers
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT,
        pincode TEXT NOT NULL,
        customer_type TEXT DEFAULT 'Retail',
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 7. Orders
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        customer_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
        subtotal REAL NOT NULL DEFAULT 0.00 CHECK (subtotal >= 0),
        tax_amount REAL NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
        discount_amount REAL NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
        total_amount REAL NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
        payment_status TEXT DEFAULT 'Unpaid' CHECK (payment_status IN ('Unpaid', 'Paid', 'Refunded')),
        notes TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
    );

    -- 8. Order Items
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price REAL NOT NULL CHECK (unit_price > 0),
        subtotal REAL NOT NULL CHECK (subtotal > 0),
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
    );

    -- 9. Shipments
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL UNIQUE,
        warehouse_id INTEGER NOT NULL,
        carrier TEXT NOT NULL,
        tracking_number TEXT NOT NULL UNIQUE,
        shipping_status TEXT DEFAULT 'Preparing',
        shipped_at TIMESTAMP,
        delivered_at TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
    );

    -- 10. Stock Transfers
    CREATE TABLE IF NOT EXISTS stock_transfers (
        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        source_warehouse_id INTEGER NOT NULL,
        destination_warehouse_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        status TEXT DEFAULT 'Requested',
        initiated_by TEXT DEFAULT 'System Admin',
        initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
        FOREIGN KEY (source_warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
        FOREIGN KEY (destination_warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
        CHECK (source_warehouse_id <> destination_warehouse_id)
    );

    -- 11. Inventory Audit Log
    CREATE TABLE IF NOT EXISTS inventory_audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        change_type TEXT NOT NULL,
        old_quantity INTEGER NOT NULL,
        new_quantity INTEGER NOT NULL,
        change_amount INTEGER NOT NULL,
        reference_id TEXT,
        changed_by TEXT DEFAULT 'SYSTEM',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
    );

    -- Performance Indexes
    CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
    CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
    CREATE INDEX IF NOT EXISTS idx_inventory_lookup ON inventory(product_id, warehouse_id);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
    CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);

    -- Views
    DROP VIEW IF EXISTS vw_low_stock_alerts;
    CREATE VIEW vw_low_stock_alerts AS
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
    WHERE i.quantity_on_hand <= p.reorder_level;

    DROP VIEW IF EXISTS vw_inventory_valuation;
    CREATE VIEW vw_inventory_valuation AS
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

    DROP VIEW IF EXISTS vw_customer_order_summary;
    CREATE VIEW vw_customer_order_summary AS
    SELECT 
        c.customer_id,
        c.full_name,
        c.email,
        c.customer_type,
        c.city,
        COUNT(o.order_id) AS total_orders_placed,
        IFNULL(SUM(CASE WHEN o.status <> 'Cancelled' THEN o.total_amount ELSE 0 END), 0.00) AS lifetime_spent,
        MAX(o.order_date) AS most_recent_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.full_name, c.email, c.customer_type, c.city;

    -- Triggers for Audit Logging & Stock Constraints
    DROP TRIGGER IF EXISTS trg_audit_inventory_update;
    CREATE TRIGGER trg_audit_inventory_update
    AFTER UPDATE OF quantity_on_hand ON inventory
    FOR EACH ROW
    WHEN NEW.quantity_on_hand <> OLD.quantity_on_hand
    BEGIN
        INSERT INTO inventory_audit_log (
            product_id, warehouse_id, change_type, old_quantity, new_quantity, change_amount, reference_id, changed_by, timestamp
        ) VALUES (
            NEW.product_id,
            NEW.warehouse_id,
            CASE 
                WHEN NEW.quantity_on_hand < OLD.quantity_on_hand THEN 'ORDER_DEDUCT'
                ELSE 'RESTOCK'
            END,
            OLD.quantity_on_hand,
            NEW.quantity_on_hand,
            NEW.quantity_on_hand - OLD.quantity_on_hand,
            'SYSTEM-AUTO',
            'SYSTEM_TRIGGER',
            datetime('now')
        );
    END;
    """)

    conn.commit()
    conn.close()

def seed_sample_data() -> None:
    """Inserts mock data if categories table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM categories;")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    cursor.executescript("""
    -- 1. Categories
    INSERT INTO categories (category_name, description) VALUES
    ('Consumer Electronics', 'Smartphones, laptops, tablets, audio accessories, and peripherals'),
    ('Office Equipment', 'Printers, ergonomic furniture, paper goods, and stationery'),
    ('Industrial Supplies', 'Power tools, safety gear, fasteners, and storage racks'),
    ('Apparel & Footwear', 'Work uniforms, safety boots, and branded corporate merchandise'),
    ('Packaged Foods & Beverages', 'Non-perishable snack packs, bottled beverages, and pantry items');

    -- 2. Suppliers
    INSERT INTO suppliers (company_name, contact_person, email, phone, address, city, country, rating) VALUES
    ('Apex Tech Logix Ltd', 'Rajesh Sharma', 'orders@apextech.in', '+91-9820011223', 'Plot 42, MIDC Andheri', 'Mumbai', 'India', 4.8),
    ('Zenith Industrial Tools', 'Priya Nambiar', 'sales@zenithtools.com', '+91-9845012345', 'Peenya Phase II', 'Bengaluru', 'India', 4.5),
    ('Delta Office Corp', 'Amitabh Verma', 'support@deltaoffice.in', '+91-9811098765', 'Okhla Phase III', 'New Delhi', 'India', 4.2),
    ('Global Wear Innovations', 'Sunita Reddy', 'contact@globalwear.co.in', '+91-9988776655', 'Cherlapally Estate', 'Hyderabad', 'India', 4.6),
    ('Heritage Refreshments', 'Karan Patel', 'supply@heritagerefresh.com', '+91-9876543210', 'Sanand GIDC', 'Ahmedabad', 'India', 4.4);

    -- 3. Warehouses
    INSERT INTO warehouses (warehouse_code, warehouse_name, location_city, capacity_sqft, manager_name, contact_phone) VALUES
    ('WH-BOM-01', 'Mumbai Central Logistics Hub', 'Mumbai', 45000, 'Vikram Malhotra', '+91-9821055443'),
    ('WH-BLR-01', 'Bengaluru Tech Park Warehouse', 'Bengaluru', 38000, 'Deepa Krishnan', '+91-9844066554'),
    ('WH-DEL-01', 'Delhi-NCR Distribution Center', 'Gurugram', 50000, 'Rohan Kapoor', '+91-9811077665'),
    ('WH-HYD-01', 'Hyderabad South Fulfillment Center', 'Hyderabad', 30000, 'Ananya Rao', '+91-9949088776');

    -- 4. Products
    INSERT INTO products (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level) VALUES
    ('TECH-MBP-14', 'MacBook Pro 14" M3 (16GB, 512GB)', 1, 1, 145000.00, 169900.00, 10),
    ('TECH-DELL-XPS', 'Dell XPS 13 Plus Laptop', 1, 1, 110000.00, 134990.00, 8),
    ('TECH-SNY-WH1000', 'Sony WH-1000XM5 Noise Cancelling Headphones', 1, 1, 21000.00, 29990.00, 20),
    ('TECH-LOGI-MX', 'Logitech MX Master 3S Wireless Mouse', 1, 1, 6200.00, 8995.00, 25),
    ('OFF-CHAIR-ERGO', 'Ergonomic Mesh High-Back Office Chair', 2, 3, 7500.00, 12499.00, 15),
    ('OFF-DESK-STAND', 'Motorized Dual-Motor Standing Desk (140x70cm)', 2, 3, 18000.00, 26999.00, 6),
    ('OFF-PRNT-HP', 'HP LaserJet Pro Multifunction Duplex Printer', 2, 3, 14000.00, 19800.00, 10),
    ('IND-DRILL-BSH', 'Bosch Professional 18V Cordless Impact Drill Kit', 3, 2, 8500.00, 12200.00, 12),
    ('IND-SAFETY-BOOT', 'Steel-Toe Kevlar Puncture-Proof Safety Boots', 3, 2, 1800.00, 2850.00, 30),
    ('IND-TOOLBOX-MET', 'Heavy-Duty 5-Tray Cantilever Metal Tool Box', 3, 2, 2200.00, 3450.00, 15),
    ('APP-JACKET-HI', 'High-Visibility Water-Resistant Safety Parka', 4, 4, 1200.00, 2100.00, 25),
    ('APP-POLO-CORP', 'Quick-Dry Corporate Pique Polo T-Shirt', 4, 4, 450.00, 899.00, 50),
    ('FND-COFFEE-BEANS', 'Premium Arabica Whole Roast Coffee Beans (1kg)', 5, 5, 650.00, 1150.00, 40),
    ('FND-TEA-DARJ', 'Single-Estate Darjeeling First Flush Tea (500g)', 5, 5, 520.00, 950.00, 35),
    ('FND-ENERGY-BAR', 'Nut & Seed High-Protein Granola Bars (Box of 24)', 5, 5, 780.00, 1350.00, 30);

    -- 5. Inventory
    INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, bin_location, last_restocked_at) VALUES
    (1, 1, 18, 'A-01-01', datetime('now')),
    (2, 1, 5,  'A-01-02', datetime('now')),
    (3, 1, 32, 'A-02-01', datetime('now')),
    (4, 1, 60, 'A-02-02', datetime('now')),
    (5, 1, 20, 'B-01-01', datetime('now')),
    (8, 1, 14, 'C-01-01', datetime('now')),
    (13, 1, 80, 'D-01-01', datetime('now')),

    (1, 2, 12, 'BLR-E1', datetime('now')),
    (2, 2, 0,  'BLR-E2', datetime('now')),
    (3, 2, 15, 'BLR-E3', datetime('now')),
    (4, 2, 45, 'BLR-E4', datetime('now')),
    (6, 2, 9,  'BLR-F1', datetime('now')),
    (7, 2, 14, 'BLR-F2', datetime('now')),
    (9, 2, 55, 'BLR-G1', datetime('now')),
    (12, 2, 120, 'BLR-H1', datetime('now')),

    (1, 3, 8,  'DEL-A1', datetime('now')),
    (5, 3, 25, 'DEL-B1', datetime('now')),
    (6, 3, 4,  'DEL-B2', datetime('now')),
    (7, 3, 18, 'DEL-B3', datetime('now')),
    (8, 3, 22, 'DEL-C1', datetime('now')),
    (10, 3, 40, 'DEL-C2', datetime('now')),
    (11, 3, 35, 'DEL-D1', datetime('now')),

    (3, 4, 18, 'HYD-01', datetime('now')),
    (4, 4, 30, 'HYD-02', datetime('now')),
    (9, 4, 28, 'HYD-03', datetime('now')),
    (13, 4, 50, 'HYD-04', datetime('now')),
    (14, 4, 60, 'HYD-05', datetime('now')),
    (15, 4, 45, 'HYD-06', datetime('now'));

    -- 6. Customers
    INSERT INTO customers (full_name, email, phone, shipping_address, city, state, pincode, customer_type) VALUES
    ('Aditya Deshmukh', 'aditya.deshmukh@gmail.com', '+91-9820123456', 'Flat 402, Sea Breeze, Worli', 'Mumbai', 'Maharashtra', '400018', 'Retail'),
    ('Kavita Raman', 'kavita.raman@infosys.com', '+91-9845987654', 'B-12, Palm Meadows, Whitefield', 'Bengaluru', 'Karnataka', '560066', 'Corporate'),
    ('Siddharth Khanna', 'siddharth@khannalaw.in', '+91-9811456789', '44 Golf Links', 'New Delhi', 'Delhi', '110003', 'Retail'),
    ('Meera Swaminathan', 'procurement@swamitech.org', '+91-9949112233', 'Plot 18, HITEC City', 'Hyderabad', 'Telangana', '500081', 'Wholesale'),
    ('Nitin Chawla', 'nitin.chawla@startuphub.io', '+91-9871098765', 'Sector 54, Golf Course Rd', 'Gurugram', 'Haryana', '122002', 'Corporate'),
    ('Pooja Singhal', 'pooja.s@gmail.com', '+91-9765432109', '14 Navrangpura', 'Ahmedabad', 'Gujarat', '380009', 'Retail');

    -- 7. Orders
    INSERT INTO orders (order_number, customer_id, order_date, status, subtotal, tax_amount, discount_amount, total_amount, payment_status, notes) VALUES
    ('ORD-2026-001', 1, '2026-11-01 10:30:00', 'Delivered', 178895.00, 32201.10, 2000.00, 209096.10, 'Paid', 'Deliver after 5 PM'),
    ('ORD-2026-002', 2, '2026-11-05 14:15:00', 'Delivered', 76497.00, 13769.46, 1500.00, 88766.46, 'Paid', 'Corporate invoicing requested'),
    ('ORD-2026-003', 3, '2026-11-10 11:45:00', 'Shipped', 49790.00, 8962.20, 0.00, 58752.20, 'Paid', 'Express air delivery'),
    ('ORD-2026-004', 4, '2026-11-12 16:20:00', 'Processing', 94500.00, 17010.00, 3500.00, 108010.00, 'Paid', 'Wholesale bulk consignment'),
    ('ORD-2026-005', 5, '2026-11-18 09:10:00', 'Pending', 53998.00, 9719.64, 1000.00, 62717.64, 'Unpaid', 'Awaiting NEFT wire confirmation');

    -- 8. Order Items
    INSERT INTO order_items (order_id, product_id, warehouse_id, quantity, unit_price, subtotal) VALUES
    (1, 1, 1, 1, 169900.00, 169900.00),
    (1, 4, 1, 1, 8995.00, 8995.00),
    (2, 5, 2, 2, 12499.00, 24998.00),
    (2, 6, 2, 1, 26999.00, 26999.00),
    (2, 7, 2, 1, 19800.00, 19800.00),
    (3, 3, 3, 1, 29990.00, 29990.00),
    (3, 7, 3, 1, 19800.00, 19800.00),
    (4, 9, 4, 30, 2850.00, 85500.00),
    (4, 12, 4, 10, 899.00, 8990.00),
    (5, 6, 3, 2, 26999.00, 53998.00);

    -- 9. Shipments
    INSERT INTO shipments (order_id, warehouse_id, carrier, tracking_number, shipping_status, shipped_at, delivered_at) VALUES
    (1, 1, 'BlueDart Express', 'BD-982347102', 'Delivered', '2026-11-01 16:00:00', '2026-11-03 11:30:00'),
    (2, 2, 'Delhivery Logistics', 'DL-554192083', 'Delivered', '2026-11-06 09:00:00', '2026-11-08 15:45:00'),
    (3, 3, 'DTDC Air Cargo', 'DT-112093481', 'In Transit', '2026-11-10 18:00:00', NULL);

    -- 10. Stock Transfers
    INSERT INTO stock_transfers (product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, completed_at) VALUES
    (1, 1, 2, 3, 'Completed', 'Supply Chain Mgr', '2026-11-04 14:00:00'),
    (3, 1, 4, 5, 'Completed', 'Supply Chain Mgr', '2026-11-08 12:30:00'),
    (8, 3, 1, 4, 'In Transit', 'Logistics Lead', NULL);

    -- 11. Initial Audit Log
    INSERT INTO inventory_audit_log (product_id, warehouse_id, change_type, old_quantity, new_quantity, change_amount, reference_id, changed_by) VALUES
    (1, 1, 'RESTOCK', 10, 20, 10, 'PO-2026-101', 'SYSTEM'),
    (1, 1, 'ORDER_DEDUCT', 20, 19, -1, 'ORD-2026-001', 'SYSTEM'),
    (1, 1, 'TRANSFER_OUT', 19, 16, -3, 'TRF-001', 'Admin_Vikram'),
    (1, 2, 'TRANSFER_IN', 9, 12, 3, 'TRF-001', 'Admin_Deepa'),
    (2, 2, 'ORDER_DEDUCT', 2, 0, -2, 'ORD-LEGACY', 'SYSTEM');
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Initializing StockFlow Database...")
    init_database()
    print("Database schema created successfully.")
    print("Seeding initial dataset...")
    seed_sample_data()
    print("StockFlow Database is ready at database/stockflow.db")
