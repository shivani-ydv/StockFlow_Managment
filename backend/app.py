"""
StockFlow - Smart Inventory & Order Management System
Flask REST API Backend demonstrating DBMS principles:
ACID transactions, Views, Raw SQL joins, Constraints, and Trigger-based audits.
"""

import os
import sys
import time
import io
import csv
import json
import urllib.request
import urllib.error
import sqlite3

# Ensure local backend modules can be imported from any working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db import get_db_connection, init_database, seed_sample_data

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

# Ensure DB is initialized on startup
init_database()
seed_sample_data()

@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ============================================================================
# API Endpoints
# ============================================================================

@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Returns aggregated KPIs and chart datasets."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products;")
    total_products = cursor.fetchone()[0]

    # Total Warehouses
    cursor.execute("SELECT COUNT(*) FROM warehouses WHERE is_operational = 1;")
    total_warehouses = cursor.fetchone()[0]

    # Total Inventory Units & Valuation
    cursor.execute("""
        SELECT 
            IFNULL(SUM(i.quantity_on_hand), 0) AS total_units,
            ROUND(IFNULL(SUM(i.quantity_on_hand * p.cost_price), 0), 2) AS total_cost_value,
            ROUND(IFNULL(SUM(i.quantity_on_hand * p.unit_price), 0), 2) AS total_retail_value
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id;
    """)
    val_row = cursor.fetchone()
    total_units = val_row["total_units"]
    total_cost_val = val_row["total_cost_value"]
    total_retail_val = val_row["total_retail_value"]

    # Low Stock Alerts Count from View
    cursor.execute("SELECT COUNT(*) FROM vw_low_stock_alerts;")
    low_stock_count = cursor.fetchone()[0]

    # Total Orders Count
    cursor.execute("SELECT COUNT(*), IFNULL(SUM(total_amount), 0) FROM orders WHERE status <> 'Cancelled';")
    order_stats = cursor.fetchone()
    total_orders = order_stats[0]
    total_revenue = round(order_stats[1], 2)

    # Chart 1: Stock by Category
    cursor.execute("""
        SELECT c.category_name, SUM(i.quantity_on_hand) AS total_stock
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_name;
    """)
    category_stock = [dict(row) for row in cursor.fetchall()]

    # Chart 2: Stock by Warehouse
    cursor.execute("""
        SELECT w.warehouse_name, w.location_city, SUM(i.quantity_on_hand) AS total_stock
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        GROUP BY w.warehouse_name, w.location_city;
    """)
    warehouse_stock = [dict(row) for row in cursor.fetchall()]

    # Recent Audit Logs
    cursor.execute("""
        SELECT a.*, p.product_name, w.warehouse_name
        FROM inventory_audit_log a
        JOIN products p ON a.product_id = p.product_id
        JOIN warehouses w ON a.warehouse_id = w.warehouse_id
        ORDER BY a.log_id DESC LIMIT 6;
    """)
    recent_audits = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "total_products": total_products,
        "total_warehouses": total_warehouses,
        "total_units": total_units,
        "total_cost_value": total_cost_val,
        "total_retail_value": total_retail_val,
        "low_stock_count": low_stock_count,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "category_stock": category_stock,
        "warehouse_stock": warehouse_stock,
        "recent_audits": recent_audits
    })

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    """Lists inventory items with multi-table joins and optional filters."""
    warehouse_id = request.args.get("warehouse_id")
    category_id = request.args.get("category_id")
    search = request.args.get("search", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            i.inventory_id,
            p.product_id,
            p.sku,
            p.barcode,
            p.product_name,
            c.category_name,
            s.company_name AS supplier_name,
            w.warehouse_id,
            w.warehouse_name,
            w.location_city,
            i.quantity_on_hand,
            p.reorder_level,
            p.unit_price,
            p.cost_price,
            i.bin_location,
            i.last_restocked_at,
            CASE 
                WHEN i.quantity_on_hand = 0 THEN 'OUT_OF_STOCK'
                WHEN i.quantity_on_hand <= (p.reorder_level / 2) THEN 'CRITICAL'
                WHEN i.quantity_on_hand <= p.reorder_level THEN 'LOW_STOCK'
                ELSE 'HEALTHY'
            END AS stock_status
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        WHERE 1=1
    """
    params = []

    if warehouse_id:
        query += " AND i.warehouse_id = ?"
        params.append(warehouse_id)
    if category_id:
        query += " AND p.category_id = ?"
        params.append(category_id)
    if search:
        query += " AND (p.product_name LIKE ? OR p.sku LIKE ? OR p.barcode LIKE ? OR w.location_city LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY p.product_name, w.warehouse_name;"
    cursor.execute(query, params)
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"inventory": items})

@app.route("/api/low-stock", methods=["GET"])
def get_low_stock_view():
    """Queries the database view vw_low_stock_alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vw_low_stock_alerts;")
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"alerts": alerts})

@app.route("/api/products", methods=["GET"])
def get_products():
    """Retrieves product catalog with pricing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, c.category_name, s.company_name AS supplier_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id;
    """)
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"products": products})

@app.route("/api/warehouses", methods=["GET"])
def get_warehouses():
    """Retrieves list of warehouses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warehouses WHERE is_operational = 1 ORDER BY warehouse_id;")
    warehouses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"warehouses": warehouses})

@app.route("/api/customers", methods=["GET"])
def get_customers():
    """Retrieves list of customers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY full_name;")
    customers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"customers": customers})

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Retrieves list of product categories."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY category_id;")
    cats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"categories": cats})

@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Retrieves orders with customer details and line count."""
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            o.order_id,
            o.order_number,
            o.order_date,
            o.status,
            o.total_amount,
            o.subtotal,
            o.tax_amount,
            o.payment_status,
            c.full_name AS customer_name,
            c.city AS customer_city,
            c.customer_type,
            COUNT(oi.order_item_id) AS items_count,
            s.carrier,
            s.tracking_number,
            s.shipping_status
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN shipments s ON o.order_id = s.order_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND o.status = ?"
        params.append(status_filter)
    if search:
        query += " AND (o.order_number LIKE ? OR c.full_name LIKE ? OR c.city LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += """
        GROUP BY o.order_id
        ORDER BY o.order_date DESC;
    """
    cursor.execute(query, params)
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"orders": orders})

@app.route("/api/orders", methods=["POST"])
def place_order():
    """
    ACID Transaction demonstration for order placement.
    Atomically verifies inventory stock, deducts stock, creates order & order_items.
    Rolls back automatically on insufficient stock or invalid inputs.
    """
    data = request.get_json()
    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id")
    quantity = int(data.get("quantity", 0))
    notes = data.get("notes", "Online Web Order")

    if quantity <= 0:
        return jsonify({"success": False, "error": "Order quantity must be positive."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Verify product price
        cursor.execute("SELECT unit_price, product_name FROM products WHERE product_id = ? AND is_active = 1;", (product_id,))
        prod = cursor.fetchone()
        if not prod:
            return jsonify({"success": False, "error": "Product not found or inactive."}), 404
        
        unit_price = prod["unit_price"]
        prod_name = prod["product_name"]

        # Step 2: Check Inventory stock (ACID Lock / Verification)
        cursor.execute("""
            SELECT quantity_on_hand FROM inventory 
            WHERE product_id = ? AND warehouse_id = ?;
        """, (product_id, warehouse_id))
        inv_row = cursor.fetchone()

        if not inv_row:
            return jsonify({"success": False, "error": "Selected warehouse does not stock this product."}), 400

        current_stock = inv_row["quantity_on_hand"]
        if current_stock < quantity:
            # Transaction Abort: Demonstrates rollback on business rule violation
            return jsonify({
                "success": False, 
                "error": f"Insufficient stock! Available in this warehouse: {current_stock} units. Requested: {quantity} units."
            }), 400

        # Step 3: Atomic Deduct Inventory
        cursor.execute("""
            UPDATE inventory 
            SET quantity_on_hand = quantity_on_hand - ? 
            WHERE product_id = ? AND warehouse_id = ?;
        """, (quantity, product_id, warehouse_id))

        # Step 4: Calculate subtotal & tax (18% GST)
        subtotal = round(unit_price * quantity, 2)
        tax = round(subtotal * 0.18, 2)
        total = round(subtotal + tax, 2)
        order_number = f"ORD-{int(time.time())}-{int(product_id)}"

        cursor.execute("""
            INSERT INTO orders (order_number, customer_id, order_date, status, subtotal, tax_amount, total_amount, payment_status, notes)
            VALUES (?, ?, datetime('now'), 'Processing', ?, ?, ?, 'Paid', ?);
        """, (order_number, customer_id, subtotal, tax, total, notes))

        order_id = cursor.lastrowid

        # Step 5: Insert Order Item
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (order_id, product_id, warehouse_id, quantity, unit_price, subtotal))

        # Step 6: Record Movement into Event Ledger (Event Sourcing)
        balance_after = current_stock - quantity
        cursor.execute("""
            INSERT INTO inventory_ledger (
                product_id, warehouse_id, movement_type, delta_quantity, balance_after,
                reference_type, reference_id, notes, recorded_by
            ) VALUES (?, ?, 'SALE', ?, ?, 'ORDER', ?, ?, 'ACID_CHECKOUT');
        """, (product_id, warehouse_id, -quantity, balance_after, order_number, f"Order {order_number} checkout"))

        # Step 7: Commit Transaction
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Order {order_number} successfully placed!",
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"Transaction rolled back: {str(e)}"}), 500

@app.route("/api/transfers", methods=["GET"])
def get_transfers():
    """Retrieves list of inter-warehouse stock transfers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.transfer_id,
            t.quantity,
            t.status,
            t.initiated_by,
            t.initiated_at,
            t.completed_at,
            p.product_id,
            p.product_name,
            p.sku,
            w1.warehouse_name AS source_warehouse,
            w1.location_city AS source_city,
            w2.warehouse_name AS destination_warehouse,
            w2.location_city AS destination_city
        FROM stock_transfers t
        JOIN products p ON t.product_id = p.product_id
        JOIN warehouses w1 ON t.source_warehouse_id = w1.warehouse_id
        JOIN warehouses w2 ON t.destination_warehouse_id = w2.warehouse_id
        ORDER BY t.transfer_id DESC;
    """)
    transfers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"transfers": transfers})

@app.route("/api/transfers", methods=["POST"])
def transfer_stock():
    """
    ACID Transaction for inter-warehouse stock transfer with Event Ledger recording.
    """
    data = request.get_json()
    product_id = data.get("product_id")
    from_wh = data.get("from_warehouse_id")
    to_wh = data.get("to_warehouse_id")
    quantity = int(data.get("quantity", 0))

    if from_wh == to_wh:
        return jsonify({"success": False, "error": "Source and destination warehouses cannot be identical."}), 400
    if quantity <= 0:
        return jsonify({"success": False, "error": "Transfer quantity must be greater than zero."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check source stock
        cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", (product_id, from_wh))
        src_row = cursor.fetchone()
        if not src_row or src_row["quantity_on_hand"] < quantity:
            avail = src_row["quantity_on_hand"] if src_row else 0
            return jsonify({"success": False, "error": f"Source warehouse does not have enough stock (Available: {avail})."}), 400

        src_bal = src_row["quantity_on_hand"] - quantity

        # Deduct from source
        cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand - ? WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, from_wh))

        # Check or add to destination
        cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", (product_id, to_wh))
        dst_row = cursor.fetchone()
        if dst_row:
            dst_bal = dst_row["quantity_on_hand"] + quantity
            cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now') WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, to_wh))
        else:
            dst_bal = quantity
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at) VALUES (?, ?, ?, datetime('now'));", (product_id, to_wh, quantity))

        # Record transfer log
        cursor.execute("""
            INSERT INTO stock_transfers (product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, completed_at)
            VALUES (?, ?, ?, ?, 'Completed', 'Web Admin', datetime('now'));
        """, (product_id, from_wh, to_wh, quantity))
        transfer_id = cursor.lastrowid

        # Write Double-Entry movements to Event Ledger
        cursor.execute("""
            INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by)
            VALUES (?, ?, 'TRANSFER_OUT', ?, ?, 'TRANSFER', ?, ?, 'Transfer Out');
        """, (product_id, from_wh, -quantity, src_bal, f"TRF-{transfer_id}", f"Transferred out to WH #{to_wh}"))

        cursor.execute("""
            INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by)
            VALUES (?, ?, 'TRANSFER_IN', ?, ?, 'TRANSFER', ?, ?, 'Transfer In');
        """, (product_id, to_wh, quantity, dst_bal, f"TRF-{transfer_id}", f"Received from WH #{from_wh}"))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully transferred {quantity} units between warehouses."})

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"Transfer failed and was rolled back: {str(e)}"}), 500

@app.route("/api/restock", methods=["POST"])
def restock_product():
    """Restocks inventory in a warehouse and logs to Event Ledger."""
    data = request.get_json()
    product_id = data.get("product_id")
    warehouse_id = data.get("warehouse_id")
    quantity = int(data.get("quantity", 0))

    if quantity <= 0:
        return jsonify({"success": False, "error": "Restock quantity must be positive."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", (product_id, warehouse_id))
        row = cursor.fetchone()
        if row:
            new_bal = row["quantity_on_hand"] + quantity
            cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now') WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, warehouse_id))
        else:
            new_bal = quantity
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at) VALUES (?, ?, ?, datetime('now'));", (product_id, warehouse_id, quantity))

        # Record RESTOCK event into inventory_ledger
        cursor.execute("""
            INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by)
            VALUES (?, ?, 'RESTOCK', ?, ?, 'MANUAL_RESTOCK', ?, 'Manual warehouse replenishment', 'Web Admin');
        """, (product_id, warehouse_id, quantity, new_bal, f"RESTOCK-{int(time.time())}"))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully added {quantity} units to inventory."})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    """Retrieves immutable audit logs generated by database triggers."""
    change_type = request.args.get("change_type", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT a.*, p.product_name, p.sku, w.warehouse_name, w.location_city
        FROM inventory_audit_log a
        JOIN products p ON a.product_id = p.product_id
        JOIN warehouses w ON a.warehouse_id = w.warehouse_id
        WHERE 1=1
    """
    params = []
    if change_type:
        query += " AND a.change_type = ?"
        params.append(change_type)
    query += " ORDER BY a.log_id DESC LIMIT 100;"
    cursor.execute(query, params)
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"audit_logs": logs})

# ============================================================================
# Step 2: CSV Bulk Upload & Sample Template
# ============================================================================

@app.route("/api/inventory/sample-csv", methods=["GET"])
def get_sample_csv():
    """Generates a downloadable sample CSV template for inventory imports."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["sku", "product_name", "category_name", "warehouse_code", "quantity", "cost_price", "unit_price", "reorder_level", "barcode"])
    writer.writerow(["COMP-MAC-M3", "MacBook Air 15\" M3 (16GB, 512GB)", "Enterprise Computing & Servers", "WH-BOM-01", "20", "115000", "134900", "8", "8901030991122"])
    writer.writerow(["NET-CAT6-DRUM", "Belden Cat6 305m Shielded Cable Spool", "Data & Telecom Infrastructure", "WH-BLR-01", "35", "8500", "12500", "10", "8901030991133"])
    writer.writerow(["IND-GRND-MAK", "Makita 4-1/2\" Angle Grinder 840W", "Industrial Automation & Tools", "WH-PNQ-01", "40", "4200", "6499", "15", "8901030991144"])
    writer.writerow(["SAF-VEST-HIGH", "High-Visibility 3M Reflective Safety Vest", "Occupational Safety & Gear", "WH-DEL-01", "100", "350", "799", "30", "8901030991155"])
    writer.writerow(["MED-BURN-KIT", "BurnKare Industrial Hydrogel Burn Care Pack", "Medical & First Aid", "WH-HYD-01", "25", "1800", "2800", "10", "8901030991166"])
    
    csv_text = output.getvalue()
    return csv_text, 200, {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=stockflow_inventory_sample.csv"
    }

@app.route("/api/inventory/upload-csv", methods=["POST"])
def upload_csv_inventory():
    """
    Step 2: CSV Bulk Importer with Row Validation and Single-Transaction Protection.
    Validates all rows first; if clean, wraps all inserts in START TRANSACTION ... COMMIT.
    """
    csv_content = None
    if "file" in request.files:
        file = request.files["file"]
        csv_content = file.read().decode("utf-8", errors="replace")
    elif request.is_json:
        csv_content = request.get_json().get("csv_content", "")
    elif request.data:
        csv_content = request.data.decode("utf-8", errors="replace")

    if not csv_content or not csv_content.strip():
        return jsonify({"success": False, "error": "No CSV content provided."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Pre-load warehouse lookup map
    cursor.execute("SELECT warehouse_id, warehouse_code FROM warehouses;")
    warehouse_map = {row["warehouse_code"].strip().upper(): row["warehouse_id"] for row in cursor.fetchall()}

    # Pre-load categories
    cursor.execute("SELECT category_id, category_name FROM categories;")
    category_map = {row["category_name"].strip().lower(): row["category_id"] for row in cursor.fetchall()}

    # Pre-load existing suppliers (default to supplier #1 if unspecified)
    cursor.execute("SELECT supplier_id FROM suppliers LIMIT 1;")
    default_supplier_row = cursor.fetchone()
    default_supplier_id = default_supplier_row[0] if default_supplier_row else 1

    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    required_cols = {"sku", "product_name", "warehouse_code", "quantity"}
    if not required_cols.issubset(set([col.strip().lower() for col in (reader.fieldnames or [])])):
        conn.close()
        return jsonify({
            "success": False,
            "error": f"Invalid CSV headers! Required columns: {', '.join(required_cols)}. Found: {', '.join(reader.fieldnames or [])}"
        }), 400

    rows_to_import = []
    validation_errors = []
    seen_skus = set()

    for idx, row in enumerate(reader, start=2): # Line 2 is first data row
        # Normalize keys
        cleaned_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}

        sku = cleaned_row.get("sku")
        p_name = cleaned_row.get("product_name")
        wh_code = cleaned_row.get("warehouse_code", "").upper()
        qty_str = cleaned_row.get("quantity")
        cost_str = cleaned_row.get("cost_price", "0")
        unit_str = cleaned_row.get("unit_price", "0")
        reorder_str = cleaned_row.get("reorder_level", "15")
        barcode = cleaned_row.get("barcode", "") or None
        cat_name = cleaned_row.get("category_name", "General Merchandise")

        # Row Validation 1: Mandatory fields
        if not sku:
            validation_errors.append({"row": idx, "field": "sku", "message": "SKU cannot be empty."})
            continue
        if not p_name:
            validation_errors.append({"row": idx, "field": "product_name", "message": "Product name cannot be empty."})
            continue

        # Row Validation 2: Warehouse existence
        if wh_code not in warehouse_map:
            validation_errors.append({
                "row": idx, 
                "field": "warehouse_code", 
                "message": f"Warehouse code '{wh_code}' is not recognized. Valid codes: {', '.join(warehouse_map.keys())}"
            })
            continue

        # Row Validation 3: Non-negative quantity
        try:
            qty = int(qty_str)
            if qty < 0:
                validation_errors.append({"row": idx, "field": "quantity", "message": f"Negative stock count ({qty}) is illegal."})
                continue
        except (ValueError, TypeError):
            validation_errors.append({"row": idx, "field": "quantity", "message": f"Quantity '{qty_str}' is not a valid integer."})
            continue

        # Row Validation 4: Prices
        try:
            cost = float(cost_str) if cost_str else 0.0
            unit = float(unit_str) if unit_str else cost * 1.25
            if cost < 0 or unit < 0:
                validation_errors.append({"row": idx, "field": "price", "message": "Prices cannot be negative."})
                continue
            if unit < cost:
                validation_errors.append({"row": idx, "field": "unit_price", "message": f"Unit price (₹{unit}) cannot be lower than cost price (₹{cost})."})
                continue
        except ValueError:
            validation_errors.append({"row": idx, "field": "price", "message": "Invalid price numeric format."})
            continue

        reorder = int(reorder_str) if reorder_str and reorder_str.isdigit() else 15

        rows_to_import.append({
            "sku": sku,
            "product_name": p_name,
            "barcode": barcode,
            "category_name": cat_name,
            "warehouse_id": warehouse_map[wh_code],
            "warehouse_code": wh_code,
            "quantity": qty,
            "cost_price": cost,
            "unit_price": unit,
            "reorder_level": reorder
        })

    # If any row failed validation, abort and reject the entire batch! (ACID Guarantee)
    if validation_errors:
        conn.close()
        return jsonify({
            "success": False,
            "error": f"CSV import validation failed with {len(validation_errors)} error(s). Transaction was NOT committed.",
            "validation_errors": validation_errors,
            "valid_rows_count": len(rows_to_import),
            "failed_rows_count": len(validation_errors)
        }), 400

    # Phase 2: Execute Atomic Import Transaction
    try:
        import_batch_id = f"CSV-BATCH-{int(time.time())}"
        imported_products = 0
        total_units_imported = 0

        for item in rows_to_import:
            # 1. Resolve or create category
            cat_id = category_map.get(item["category_name"].lower())
            if not cat_id:
                cursor.execute("INSERT INTO categories (category_name, description) VALUES (?, ?);", 
                               (item["category_name"], "Imported via CSV bulk spreadsheet"))
                cat_id = cursor.lastrowid
                category_map[item["category_name"].lower()] = cat_id

            # 2. Check if product exists by SKU
            cursor.execute("SELECT product_id FROM products WHERE sku = ?;", (item["sku"],))
            prod_row = cursor.fetchone()

            if prod_row:
                p_id = prod_row["product_id"]
                # Update price/info if specified
                cursor.execute("""
                    UPDATE products 
                    SET product_name = ?, cost_price = ?, unit_price = ?, barcode = COALESCE(?, barcode)
                    WHERE product_id = ?;
                """, (item["product_name"], item["cost_price"], item["unit_price"], item["barcode"], p_id))
            else:
                cursor.execute("""
                    INSERT INTO products (sku, barcode, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, (item["sku"], item["barcode"], item["product_name"], cat_id, default_supplier_id, item["cost_price"], item["unit_price"], item["reorder_level"]))
                p_id = cursor.lastrowid
                imported_products += 1

            # 3. Update inventory
            cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", 
                           (p_id, item["warehouse_id"]))
            inv_row = cursor.fetchone()

            if inv_row:
                new_bal = inv_row["quantity_on_hand"] + item["quantity"]
                cursor.execute("""
                    UPDATE inventory 
                    SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now')
                    WHERE product_id = ? AND warehouse_id = ?;
                """, (item["quantity"], p_id, item["warehouse_id"]))
            else:
                new_bal = item["quantity"]
                cursor.execute("""
                    INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at)
                    VALUES (?, ?, ?, datetime('now'));
                """, (p_id, item["warehouse_id"], item["quantity"]))

            # 4. Crucial Rule: Record movement into Event Ledger!
            cursor.execute("""
                INSERT INTO inventory_ledger (
                    product_id, warehouse_id, movement_type, delta_quantity, balance_after,
                    reference_type, reference_id, notes, recorded_by
                ) VALUES (?, ?, 'CSV_IMPORT', ?, ?, 'CSV_BATCH', ?, ?, 'CSV_UPLOAD_TOOL');
            """, (p_id, item["warehouse_id"], item["quantity"], new_bal, import_batch_id, f"CSV batch intake: {item['product_name']}"))

            total_units_imported += item["quantity"]

        # Commit all atomically
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Successfully imported {len(rows_to_import)} row(s) in a single atomic transaction. Recorded into event ledger.",
            "batch_id": import_batch_id,
            "rows_processed": len(rows_to_import),
            "new_products_created": imported_products,
            "total_units_added": total_units_imported
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"Database transaction failed: {str(e)}"}), 500

# ============================================================================
# Step 3: Barcode Scanner & Global Registry Lookup
# ============================================================================

# Fast built-in global product registry for offline instant demos!
OFFLINE_GLOBAL_REGISTRY = {
    "027242923485": {"name": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones", "brand": "Sony", "category": "Enterprise Computing & Servers", "suggested_price": 29990.0},
    "884116418856": {"name": "Dell XPS 13 Plus Intel Core i7 16GB RAM 512GB SSD", "brand": "Dell", "category": "Enterprise Computing & Servers", "suggested_price": 134990.0},
    "097855173362": {"name": "Logitech MX Master 3S Advanced Wireless Mouse", "brand": "Logitech", "category": "Enterprise Computing & Servers", "suggested_price": 8995.0},
    "3017620422003": {"name": "Nutella Hazelnut Spread with Cocoa 400g", "brand": "Ferrero", "category": "Facility Supplies & Breakroom", "suggested_price": 450.0},
    "7622210449283": {"name": "Oreo Original Chocolate Sandwich Cookies (Family Pack)", "brand": "Mondelez", "category": "Facility Supplies & Breakroom", "suggested_price": 180.0},
    "0316514088921": {"name": "Bosch Professional 18V Brushless Impact Drill Driver", "brand": "Bosch", "category": "Industrial Automation & Tools", "suggested_price": 19500.0},
    "051131069695": {"name": "3M Particulate Respirator N95 Half Mask (Box of 20)", "brand": "3M", "category": "Occupational Safety & Gear", "suggested_price": 1850.0},
    "8901030865412": {"name": "Tata Tea Gold Royal Taste Rich Leaf Tea 500g", "brand": "Tata Tea", "category": "Facility Supplies & Breakroom", "suggested_price": 320.0}
}

@app.route("/api/barcode/lookup", methods=["GET"])
def barcode_lookup():
    """
    Step 3: Barcode Lookup engine.
    1. Checks local StockFlow database by barcode or SKU.
    2. If missing, queries Open Food Facts API (with offline cache fallback).
    """
    code = request.args.get("code", "").strip()
    if not code:
        return jsonify({"success": False, "error": "Barcode or SKU code is required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Step 1: Check local database
    cursor.execute("""
        SELECT p.*, c.category_name, s.company_name AS supplier_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.barcode = ? OR p.sku = ?;
    """, (code, code))
    prod = cursor.fetchone()

    if prod:
        product_dict = dict(prod)
        # Fetch current stock distribution across all warehouses
        cursor.execute("""
            SELECT w.warehouse_id, w.warehouse_name, w.location_city, i.quantity_on_hand, i.bin_location
            FROM warehouses w
            LEFT JOIN inventory i ON w.warehouse_id = i.warehouse_id AND i.product_id = ?
            ORDER BY w.warehouse_id;
        """, (product_dict["product_id"],))
        stocks = [dict(r) for r in cursor.fetchall()]
        conn.close()

        return jsonify({
            "success": True,
            "found_locally": True,
            "product": product_dict,
            "stocks": stocks,
            "message": f"Found '{product_dict['product_name']}' in local database."
        })

    conn.close()

    # Step 2: Query External Free Registry (Open Food Facts API)
    external_data = None
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "StockFlow-Academic-Project/1.0"})
        with urllib.request.urlopen(req, timeout=2.5) as response:
            if response.status == 200:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == 1 and "product" in payload:
                    p_info = payload["product"]
                    external_data = {
                        "name": p_info.get("product_name") or p_info.get("product_name_en") or "Imported Product",
                        "brand": p_info.get("brands") or "External Brand",
                        "category": "Facility Supplies & Breakroom",
                        "suggested_price": 250.0
                    }
    except Exception:
        # Fallback to local offline catalog if network is disabled
        pass

    if not external_data and code in OFFLINE_GLOBAL_REGISTRY:
        external_data = OFFLINE_GLOBAL_REGISTRY[code]

    if external_data:
        return jsonify({
            "success": True,
            "found_locally": False,
            "external_match": True,
            "barcode": code,
            "suggested_product": {
                "product_name": external_data["name"],
                "sku": f"SCAN-{code[-6:]}",
                "brand": external_data["brand"],
                "category_name": external_data["category"],
                "suggested_unit_price": external_data["suggested_price"],
                "suggested_cost_price": round(external_data["suggested_price"] * 0.75, 2)
            },
            "message": f"Recognized via Global Product Registry: '{external_data['name']}'."
        })

    return jsonify({
        "success": False,
        "found_locally": False,
        "external_match": False,
        "barcode": code,
        "message": f"Barcode '{code}' not recognized. Enter details to onboard as a new product."
    })

@app.route("/api/barcode/intake", methods=["POST"])
def barcode_intake():
    """
    Live Barcode Intake: Increments existing item or onboards new item and writes to Event Ledger.
    """
    data = request.get_json()
    barcode = data.get("barcode", "").strip()
    warehouse_id = int(data.get("warehouse_id", 1))
    quantity = int(data.get("quantity", 1))

    if not barcode:
        return jsonify({"success": False, "error": "Barcode is required."}), 400
    if quantity <= 0:
        return jsonify({"success": False, "error": "Intake quantity must be positive."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE barcode = ? OR sku = ?;", (barcode, barcode))
        prod = cursor.fetchone()

        if prod:
            # Existing product: Increment stock
            p_id = prod["product_id"]
            cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", (p_id, warehouse_id))
            inv_row = cursor.fetchone()
            if inv_row:
                new_bal = inv_row["quantity_on_hand"] + quantity
                cursor.execute("""
                    UPDATE inventory SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now')
                    WHERE product_id = ? AND warehouse_id = ?;
                """, (quantity, p_id, warehouse_id))
            else:
                new_bal = quantity
                cursor.execute("""
                    INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at)
                    VALUES (?, ?, ?, datetime('now'));
                """, (p_id, warehouse_id, quantity))

            # Record into Event Ledger
            cursor.execute("""
                INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by)
                VALUES (?, ?, 'BARCODE_SCAN', ?, ?, 'BARCODE_SCANNER', ?, 'Live intake via barcode scan', 'Barcode_Terminal');
            """, (p_id, warehouse_id, quantity, new_bal, barcode))

            conn.commit()
            conn.close()
            return jsonify({
                "success": True,
                "action": "RESTOCKED",
                "message": f"Successfully incremented stock for '{prod['product_name']}' (+{quantity} units).",
                "new_balance": new_bal
            })

        else:
            # New product onboarding
            p_name = data.get("product_name") or f"Product {barcode[-6:]}"
            sku = data.get("sku") or f"BC-{barcode[-6:]}"
            cat_id = int(data.get("category_id") or 1)
            cost = float(data.get("cost_price") or 500.0)
            unit = float(data.get("unit_price") or 750.0)

            cursor.execute("""
                INSERT INTO products (sku, barcode, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level)
                VALUES (?, ?, ?, ?, 1, ?, ?, 15);
            """, (sku, barcode, p_name, cat_id, cost, unit))
            p_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at)
                VALUES (?, ?, ?, datetime('now'));
            """, (p_id, warehouse_id, quantity))

            # Record into Event Ledger
            cursor.execute("""
                INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by)
                VALUES (?, ?, 'BARCODE_SCAN', ?, ?, 'BARCODE_ONBOARD', ?, 'Initial scan and onboard', 'Barcode_Terminal');
            """, (p_id, warehouse_id, quantity, quantity, barcode))

            conn.commit()
            conn.close()
            return jsonify({
                "success": True,
                "action": "CREATED_AND_STOCKED",
                "message": f"Successfully onboarded '{p_name}' and initialized stock (+{quantity} units).",
                "new_balance": quantity
            })

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# Event Ledger & Consistency Reconciliation Endpoints
# ============================================================================

@app.route("/api/ledger", methods=["GET"])
def get_ledger():
    """
    Returns the immutable double-entry movement log.
    Filters: movement_type, warehouse_id, product_id, limit.
    """
    m_type = request.args.get("movement_type", "").strip()
    wh_id = request.args.get("warehouse_id", "").strip()
    limit = int(request.args.get("limit", 150))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            l.ledger_id,
            l.movement_type,
            l.delta_quantity,
            l.balance_after,
            l.reference_type,
            l.reference_id,
            l.notes,
            l.recorded_by,
            l.created_at,
            p.product_id,
            p.product_name,
            p.sku,
            p.barcode,
            w.warehouse_id,
            w.warehouse_name,
            w.location_city
        FROM inventory_ledger l
        JOIN products p ON l.product_id = p.product_id
        JOIN warehouses w ON l.warehouse_id = w.warehouse_id
        WHERE 1=1
    """
    params = []
    if m_type:
        query += " AND l.movement_type = ?"
        params.append(m_type)
    if wh_id:
        query += " AND l.warehouse_id = ?"
        params.append(wh_id)

    query += " ORDER BY l.ledger_id DESC LIMIT ?;"
    params.append(limit)

    cursor.execute(query, params)
    movements = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"ledger": movements, "total_records": len(movements)})

@app.route("/api/ledger/reconciliation", methods=["GET"])
def get_ledger_reconciliation():
    """
    Compares SUM(delta_quantity) from Event Ledger with inventory.quantity_on_hand.
    Demonstrates zero discrepancy & mathematical consistency for DBMS viva.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            p.sku,
            p.product_name,
            w.location_city,
            i.quantity_on_hand AS materialized_stock,
            IFNULL(l_sum.calculated_stock, 0) AS ledger_calculated_stock,
            (i.quantity_on_hand - IFNULL(l_sum.calculated_stock, 0)) AS discrepancy
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        LEFT JOIN (
            SELECT product_id, warehouse_id, SUM(delta_quantity) AS calculated_stock
            FROM inventory_ledger
            GROUP BY product_id, warehouse_id
        ) l_sum ON i.product_id = l_sum.product_id AND i.warehouse_id = l_sum.warehouse_id
        LIMIT 50;
    """
    cursor.execute(query)
    reconciliation = [dict(row) for row in cursor.fetchall()]
    conn.close()

    all_matched = all(r["discrepancy"] == 0 for r in reconciliation)

    return jsonify({
        "success": True,
        "is_consistent": all_matched,
        "sample_records": reconciliation,
        "message": "Event Ledger matches Materialized Inventory balances perfectly!" if all_matched else "Discrepancy detected."
    })

@app.route("/api/viva/query", methods=["POST"])
def execute_viva_query():
    """
    Executes preset viva queries or custom read-only queries with execution benchmarking.
    """
    data = request.get_json()
    query = data.get("query", "").strip()

    # Safety: Only allow SELECT or EXPLAIN statements in the query runner
    if not query.upper().startswith(("SELECT", "EXPLAIN", "WITH")):
        return jsonify({"success": False, "error": "Only read-only SELECT and EXPLAIN queries are permitted in the viva sandbox."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    t_start = time.perf_counter()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        t_end = time.perf_counter()
        elapsed_ms = round((t_end - t_start) * 1000, 2)

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = [dict(row) for row in rows]

        conn.close()
        return jsonify({
            "success": True,
            "columns": columns,
            "rows": results,
            "row_count": len(results),
            "execution_time_ms": elapsed_ms
        })
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    print("=" * 60)
    print("  StockFlow - Smart Inventory & Order Management System")
    print("  DBMS Academic Project (2nd Year B.Tech)")
    print("  Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
