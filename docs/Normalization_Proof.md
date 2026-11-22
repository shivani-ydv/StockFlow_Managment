# StockFlow — Formal Normalization Proof (1NF to 3NF & BCNF)

This document provides academic proof of database normalization for submission reports and viva evaluations.

---

## 1. Unnormalized Form (UNF) Representation

In an unnormalized legacy design, an entire purchase invoice was stored in a single flat file or record:

```
UNNORMALIZED_INVOICE(
    order_id, order_date, customer_name, customer_email, customer_city,
    [product_sku, product_name, category_name, supplier_name, warehouse_city, quantity, unit_price],
    total_amount
)
```

### Anomalies in UNF:
1. **Insertion Anomaly:** We cannot record a new supplier or warehouse unless an order has already been placed for one of their products.
2. **Deletion Anomaly:** If the only order containing a specific product is deleted, we lose all record of the product's existence and pricing.
3. **Update Anomaly:** If a customer changes their email or address, multiple historical rows must be modified. Inconsistency occurs if some rows are missed.

---

## 2. Conversion to First Normal Form (1NF)

### 1NF Criteria:
- No repeating groups or arrays of items.
- Every column contains atomic (indivisible) scalar values.
- A primary key uniquely identifies each tuple.

### 1NF Decomposition:
We decompose repeating order lines into separate tuples:

```
ORDERS_1NF(order_id, order_date, customer_id, customer_name, customer_email, customer_city, total_amount)
Primary Key: order_id

ORDER_ITEMS_1NF(order_id, product_id, product_name, category_id, category_name, supplier_id, supplier_name, warehouse_id, warehouse_city, quantity, unit_price, subtotal)
Composite Primary Key: (order_id, product_id, warehouse_id)
```

---

## 3. Conversion to Second Normal Form (2NF)

### 2NF Criteria:
- Relation must be in 1NF.
- No partial dependency exists: **Every non-prime attribute must be fully functionally dependent on the entire candidate key**, not a proper subset of it.

### Analysis of Dependencies in `ORDER_ITEMS_1NF`:
Candidate Key: `(order_id, product_id, warehouse_id)`

- `(order_id, product_id, warehouse_id) -> quantity, subtotal` (Full Dependency)
- `product_id -> product_name, category_id, category_name, supplier_id, supplier_name, unit_price` (**Partial Dependency!** Depends only on `product_id`, not `order_id` or `warehouse_id`).
- `warehouse_id -> warehouse_city` (**Partial Dependency!** Depends only on `warehouse_id`).

### 2NF Decomposition:
We isolate partial dependencies into their respective relations:

1. `ORDER_ITEMS(order_id, product_id, warehouse_id, quantity, unit_price, subtotal)`
2. `PRODUCTS_2NF(product_id, sku, product_name, category_id, category_name, supplier_id, supplier_name, cost_price, unit_price)`
3. `WAREHOUSES_2NF(warehouse_id, warehouse_code, warehouse_name, warehouse_city)`

Now, all non-prime attributes in `ORDER_ITEMS` depend strictly on the composite key.

---

## 4. Conversion to Third Normal Form (3NF)

### 3NF Criteria:
- Relation must be in 2NF.
- No transitive dependencies exist: For every functional dependency $X \to Y$, either:
  1. $X$ is a superkey, OR
  2. $Y$ is a prime attribute (part of a candidate key).

### Analysis of Transitive Dependencies in `PRODUCTS_2NF`:
Primary Key: `product_id`

- Functional Dependencies:
  - `product_id -> category_id`
  - `category_id -> category_name, description`
  - *Transitive Dependency:* `product_id -> category_name` via `category_id`!
  - `product_id -> supplier_id`
  - `supplier_id -> company_name, email, phone`
  - *Transitive Dependency:* `product_id -> company_name` via `supplier_id`!

### Analysis of Transitive Dependencies in `ORDERS_1NF`:
Primary Key: `order_id`
- `order_id -> customer_id`
- `customer_id -> customer_name, customer_email, customer_city`
- *Transitive Dependency:* `order_id -> customer_email` via `customer_id`!

### 3NF Decomposition:
We extract intermediate determinants into their own independent entities:

1. `CATEGORIES(category_id, category_name, description)`
   - Superkey: `category_id` (No transitive dependencies).
2. `SUPPLIERS(supplier_id, company_name, contact_person, email, phone, city, rating)`
   - Superkey: `supplier_id`.
3. `CUSTOMERS(customer_id, full_name, email, phone, shipping_address, city)`
   - Superkey: `customer_id`.
4. `PRODUCTS(product_id, sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level)`
   - Foreign Keys: `category_id -> CATEGORIES`, `supplier_id -> SUPPLIERS`.
5. `ORDERS(order_id, order_number, customer_id, order_date, status, subtotal, tax_amount, total_amount)`
   - Foreign Key: `customer_id -> CUSTOMERS`.

---

## 5. Boyce-Codd Normal Form (BCNF) Verification

### BCNF Criteria:
- A relation is in BCNF if and only if for every functional dependency $X \to Y$, **$X$ is a superkey**.
- Every relation in our final schema has only trivial functional dependencies or dependencies where the left side ($X$) is a primary or candidate key (`sku`, `order_number`, `tracking_number`, `email`, `inventory_id`, etc.).

### Conclusion:
The **StockFlow** schema is in **3NF / BCNF**, ensuring zero redundancy, optimal storage efficiency, and complete immunity against insertion, update, and deletion anomalies.
