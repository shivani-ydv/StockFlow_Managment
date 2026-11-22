"""
StockFlow - Smart Inventory & Order Management System
Flask REST API Backend demonstrating DBMS principles:
ACID transactions, Views, Raw SQL joins, Constraints, and Trigger-based audits.
"""

import os
import sys
import time
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
        query += " AND (p.product_name LIKE ? OR p.sku LIKE ? OR w.location_city LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

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

@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Retrieves orders with customer details and line count."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            o.order_id,
            o.order_number,
            o.order_date,
            o.status,
            o.total_amount,
            o.payment_status,
            c.full_name AS customer_name,
            c.city AS customer_city,
            COUNT(oi.order_item_id) AS items_count,
            s.tracking_number,
            s.shipping_status
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN shipments s ON o.order_id = s.order_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC;
    """)
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
        # Notice: Triggers will automatically capture this update into inventory_audit_log!
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

        # Step 6: Commit Transaction
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

@app.route("/api/transfers", methods=["POST"])
def transfer_stock():
    """
    ACID Transaction for inter-warehouse stock transfer.
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

        # Deduct from source
        cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand - ? WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, from_wh))

        # Check or add to destination
        cursor.execute("SELECT quantity_on_hand FROM inventory WHERE product_id = ? AND warehouse_id = ?;", (product_id, to_wh))
        dst_row = cursor.fetchone()
        if dst_row:
            cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now') WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, to_wh))
        else:
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at) VALUES (?, ?, ?, datetime('now'));", (product_id, to_wh, quantity))

        # Record transfer log
        cursor.execute("""
            INSERT INTO stock_transfers (product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, completed_at)
            VALUES (?, ?, ?, ?, 'Completed', 'Web Admin', datetime('now'));
        """, (product_id, from_wh, to_wh, quantity))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully transferred {quantity} units between warehouses."})

    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"success": False, "error": f"Transfer failed and was rolled back: {str(e)}"}), 500

@app.route("/api/restock", methods=["POST"])
def restock_product():
    """Restocks inventory in a warehouse."""
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
            cursor.execute("UPDATE inventory SET quantity_on_hand = quantity_on_hand + ?, last_restocked_at = datetime('now') WHERE product_id = ? AND warehouse_id = ?;", (quantity, product_id, warehouse_id))
        else:
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at) VALUES (?, ?, ?, datetime('now'));", (product_id, warehouse_id, quantity))

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.product_name, p.sku, w.warehouse_name, w.location_city
        FROM inventory_audit_log a
        JOIN products p ON a.product_id = p.product_id
        JOIN warehouses w ON a.warehouse_id = w.warehouse_id
        ORDER BY a.log_id DESC
        LIMIT 50;
    """)
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"audit_logs": logs})

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
