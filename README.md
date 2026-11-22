# StockFlow — Smart Inventory & Order Management System
> **Academic Database Management System (DBMS) Project**  
> Designed for **2nd Year B.Tech (CSE / IT / AI / ECE)** University Submission & Viva Defense

---

## 📌 Project Overview
**StockFlow** is a multi-warehouse inventory and order management system built to demonstrate core and advanced DBMS concepts:
- **Relational Modeling:** Entity-Relationship (ER) design, composite keys, constraints (`CHECK`, `UNIQUE`, `FOREIGN KEY ON DELETE RESTRICT/CASCADE`).
- **Formal Normalization:** Complete academic progression from Unnormalized Form (UNF) through **1NF, 2NF, 3NF, and BCNF**.
- **Transactions & Concurrency:** ACID-compliant checkout routines with row-level locking (`FOR UPDATE`) preventing negative stock and lost updates.
- **Triggers & Auditing:** Automated trigger-driven event logging (`inventory_audit_log`) and stock validation.
- **Views & Optimization:** Pre-computed views (`vw_low_stock_alerts`, `vw_inventory_valuation`) and B-Tree indexes for fast lookups.
- **Interactive UI Dashboard:** Modern, responsive SaaS interface with live charts, order creation, warehouse transfer modals, and an in-browser **Viva SQL Sandbox**.

---

## 👥 Team Work Breakdown (For 3-4 Students)

| Role | Team Member | Primary Deliverables | Viva Defense Specialization |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Database Architect** | ER diagram, Schema DDL, Constraints, Normalization proof (1NF-3NF) | Normalization theory, foreign key actions, indexing strategy. |
| **Member 2** | **SQL & Procedures Lead**| Stored procedures, triggers, views, ACID transaction test cases | Atomicity vs Isolation, trigger lifecycle, row locking. |
| **Member 3** | **Backend API Engineer**| Flask REST API, raw SQL execution, parameter sanitization | Connection pooling, preventing SQL injection, API integration. |
| **Member 4** | **Frontend & Documentation**| Web UI, Dashboard charts, Report generation, Viva preparation | System architecture demo, live query execution, user workflows. |

---

## 🚀 Quickstart (Run in 30 Seconds)

### Prerequisites
- Python 3.8+ (Python 3.13 is already installed on your system)
- (Optional) MySQL Server 8.0 & MySQL Workbench

### 1. Launch the Application
Open PowerShell or your terminal in this project root:
```bash
python backend/app.py
```

### 2. Open in Your Web Browser
Navigate to:
```
http://127.0.0.1:5000
```
The application will automatically:
1. Initialize the SQLite relational database at `database/stockflow.db`.
2. Apply all tables, constraints, foreign keys, triggers, and views.
3. Seed realistic sample products across Mumbai, Bengaluru, Delhi, and Hyderabad warehouses.
4. Launch the live interactive management dashboard with real-time charts!

---

## 🗄️ MySQL Workbench Instructions (For Lab Evaluation)

If your professor requires you to demonstrate directly in **MySQL Workbench 8.0**:
1. Open **MySQL Workbench** and connect to your local MySQL instance.
2. Open and run the SQL scripts located in the `database/` folder in this exact sequence:
   - `database/01_schema.sql` (Creates `stockflow_db`, tables, and indexes)
   - `database/02_views.sql` (Creates analytical views)
   - `database/03_triggers.sql` (Creates automated audit and validation triggers)
   - `database/04_procedures.sql` (Creates stored procedures with ACID transaction blocks)
   - `database/05_seed_data.sql` (Populates initial mock data)
   - `database/06_queries_viva.sql` (Executes 12+ curated viva queries)

---

## 📁 Repository Directory Structure

```
DBMS Project/
├── database/
│   ├── 01_schema.sql           # DDL: Tables, PKs, FKs, CHECK constraints, Indexes
│   ├── 02_views.sql            # Views: Low Stock, Inventory Valuation, Customer 360
│   ├── 03_triggers.sql         # Triggers: Audit logger, Negative stock guard, GST calculator
│   ├── 04_procedures.sql       # Stored Procedures: sp_place_order, sp_transfer, sp_restock
│   ├── 05_seed_data.sql        # Realistic multi-warehouse dataset
│   ├── 06_queries_viva.sql     # 12+ Complex Joins, Subqueries, GROUP BY, Window functions
│   └── stockflow.db            # Initialized SQLite database file
├── backend/
│   ├── app.py                  # Flask REST API backend
│   ├── db.py                   # DB connection & initialization script
│   └── requirements.txt        # Python dependency manifest
├── frontend/
│   └── index.html              # Responsive single-page dashboard with Chart.js & Tailwind
├── docs/
│   ├── ER_Diagram_and_Schema.md# Complete Data Dictionary and Cardinality
│   ├── Normalization_Proof.md  # Formal 1NF -> 2NF -> 3NF -> BCNF proof
│   └── Viva_Preparation_Guide.md# Top 25 DBMS viva questions with model answers
└── README.md                   # This project guide
```

---

## 🎯 Key Viva Demonstration Highlights
1. **Trigger Demo:** Place an order from the UI or run an update on `inventory`. Instantly switch to the **Trigger Audit Logs** tab to show the external examiner the newly created audit row with `OLD_QTY`, `NEW_QTY`, and delta.
2. **ACID Demo:** Attempt to place an order for 500 units when only 10 are available. Show how the backend catches the shortage, aborts the operation, and executes `ROLLBACK`.
3. **Correlated Subquery Demo:** Open the **Viva SQL Sandbox** tab and click Query 3 to demonstrate products whose price exceeds their category's average price in real-time.
