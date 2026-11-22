# StockFlow — Top 25 DBMS Viva Questions & Model Answers

### Question 1: What is the primary problem your project solves?
**Answer:** StockFlow provides unified, real-time inventory and order management across distributed multi-warehouse fulfillment hubs. It prevents stockouts through automated trigger alerts, ensures consistent atomic order checkouts using ACID transactions to eliminate race conditions, and maintains an immutable audit log of inventory movements.

---

### Question 2: Why did you normalize the database to 3NF instead of leaving it in 2NF?
**Answer:** In 2NF, transitive dependencies persist ($X \to Y$ and $Y \to Z$). For instance, if customer address remained in the `orders` table, changing a customer's address would either require updating hundreds of historical records or create update anomalies. By separating `customers`, `suppliers`, and `categories` into 3NF, non-prime attributes depend solely and directly on their primary keys.

---

### Question 3: How does your system demonstrate ACID properties?
**Answer:**
- **Atomicity:** In `sp_place_single_item_order` or `place_order()`, verifying stock, deducting units from `inventory`, and creating `orders` and `order_items` occur inside a single transaction block. If inventory is insufficient, the entire operation is rolled back using `ROLLBACK`.
- **Consistency:** Constraints like `CHECK (quantity_on_hand >= 0)` and foreign keys prevent illegal states or negative stock.
- **Isolation:** We employ row-level locking (`SELECT ... FOR UPDATE`) so two concurrent customers ordering the last remaining unit cannot both succeed (lost update prevention).
- **Durability:** Committed transactions are flushed to disk logs (WAL/redo log in MySQL InnoDB / SQLite).

---

### Question 4: What is the difference between a Trigger and a Stored Procedure?
**Answer:**
- A **Stored Procedure** is explicitly invoked by an application or user via `CALL procedure_name(...)`.
- A **Trigger** is automatically fired by the database engine in response to a DML event (`INSERT`, `UPDATE`, `DELETE`) on a specified table.
- In StockFlow, triggers automate auditing (`trg_audit_inventory_update`) and enforce stock sanity (`trg_prevent_negative_stock`), whereas procedures handle high-level transactional workflows (`sp_place_single_item_order`).

---

### Question 5: What is the difference between `WHERE` and `HAVING`?
**Answer:**
- `WHERE` filters individual rows **before** any aggregation takes place.
- `HAVING` filters aggregated groups **after** `GROUP BY` has evaluated summary functions like `SUM`, `AVG`, or `COUNT`.
- *Example from our project:* Finding suppliers where average product price exceeds ₹20,000 (`GROUP BY supplier_id HAVING AVG(unit_price) > 20000`).

---

### Question 6: What is a Correlated Subquery?
**Answer:** A correlated subquery is an inner query that references columns from the outer query table, executing once for every row processed by the outer query.
- *Example from StockFlow:* Selecting products whose `unit_price` is higher than the average price of products in that same category:
```sql
SELECT p1.product_name, p1.unit_price FROM products p1
WHERE p1.unit_price > (SELECT AVG(p2.unit_price) FROM products p2 WHERE p2.category_id = p1.category_id);
```

---

### Question 7: What are Views and why are they used in this project?
**Answer:** A view is a virtual table defined by a stored SQL query.
1. **Security:** Restricts direct table access and hides sensitive supplier margins or internal cost prices.
2. **Simplicity:** Complex 4-table joins (`vw_low_stock_alerts`) can be queried with a simple `SELECT * FROM vw_low_stock_alerts`.
3. **Consistency:** Guarantees uniform business logic across reporting dashboards.

---

### Question 8: What Indexes did you create and why?
**Answer:** We created composite and secondary B-Tree indexes:
1. `idx_orders_customer_date` on `orders(customer_id, order_date)` for fast customer purchase history lookups.
2. `idx_inventory_lookup` on `inventory(product_id, warehouse_id)` for sub-millisecond stock checks during high-frequency checkouts.
3. `idx_products_category` on `products(category_id)` to speed up category filtering.

---

### Question 9: What is the difference between Clustered and Non-Clustered Indexes?
**Answer:**
- **Clustered Index:** Dictates the physical order of data storage on disk. In InnoDB and SQLite, the Primary Key forms the clustered index. There can be only one clustered index per table.
- **Non-Clustered Index:** A separate structure holding sorted key values with pointers back to the clustered index (row identifier). A table can have multiple non-clustered indexes.

---

### Question 10: How do you handle database recovery if a crash occurs?
**Answer:**
1. **Transaction Logs:** InnoDB utilizes the Write-Ahead Log (WAL / Redo Log) to perform crash recovery on restart, replaying committed transactions and rolling back uncommitted ones.
2. **Backups:** Physical or logical backups via `mysqldump stockflow_db > backup.sql` paired with point-in-time recovery using MySQL Binary Logs (`binlog`).
