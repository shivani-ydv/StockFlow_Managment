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
        barcode TEXT UNIQUE,
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

    -- 12. Inventory Ledger (Double-Entry Movement Log)
    CREATE TABLE IF NOT EXISTS inventory_ledger (
        ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL CHECK (movement_type IN ('INITIAL_COUNT', 'RESTOCK', 'SALE', 'DAMAGE', 'RETURN', 'TRANSFER_IN', 'TRANSFER_OUT', 'CSV_IMPORT', 'BARCODE_SCAN')),
        delta_quantity INTEGER NOT NULL,
        balance_after INTEGER NOT NULL,
        reference_type TEXT DEFAULT 'MANUAL',
        reference_id TEXT,
        notes TEXT,
        recorded_by TEXT DEFAULT 'SYSTEM',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT
    );

    -- Performance Indexes
    CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
    CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
    CREATE INDEX IF NOT EXISTS idx_inventory_lookup ON inventory(product_id, warehouse_id);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
    CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
    CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
    CREATE INDEX IF NOT EXISTS idx_ledger_prod_wh ON inventory_ledger(product_id, warehouse_id);
    CREATE INDEX IF NOT EXISTS idx_ledger_created ON inventory_ledger(created_at);

    -- Views
    DROP VIEW IF EXISTS vw_inventory_calculated_stock;
    CREATE VIEW vw_inventory_calculated_stock AS
    SELECT 
        l.product_id,
        l.warehouse_id,
        p.product_name,
        p.sku,
        p.barcode,
        w.warehouse_name,
        w.location_city,
        SUM(l.delta_quantity) AS calculated_stock,
        COUNT(l.ledger_id) AS total_movements_count,
        MAX(l.created_at) AS last_movement_at
    FROM inventory_ledger l
    JOIN products p ON l.product_id = p.product_id
    JOIN warehouses w ON l.warehouse_id = w.warehouse_id
    GROUP BY l.product_id, l.warehouse_id;
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
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        from seed_rich_data import populate_rich_data
        populate_rich_data()

if __name__ == "__main__":
    print("Initializing StockFlow Database...")
    init_database()
    print("Database schema created successfully.")
    print("Seeding initial dataset...")
    seed_sample_data()
    print("StockFlow Database is ready at database/stockflow.db")
