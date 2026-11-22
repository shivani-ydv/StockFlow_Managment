# StockFlow — Data Dictionary & Entity-Relationship Specification

## 1. Relational Schema Data Dictionary

### Table: `categories`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `category_id` | INT / INTEGER | PK, AUTO_INCREMENT | Unique identifier for product category |
| `category_name`| VARCHAR(100) | NOT NULL, UNIQUE | Human-readable name of category |
| `description`  | TEXT | NULL | Contextual information |
| `created_at`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### Table: `suppliers`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `supplier_id` | INT / INTEGER | PK, AUTO_INCREMENT | Unique identifier for vendor |
| `company_name`| VARCHAR(150) | NOT NULL | Registered business name |
| `contact_person`| VARCHAR(100)| NULL | Account representative |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE | Vendor communication email |
| `phone` | VARCHAR(20) | NOT NULL | Contact phone number |
| `address` | TEXT | NULL | Physical mailing address |
| `city` | VARCHAR(80) | NULL | Operating city |
| `country` | VARCHAR(80) | DEFAULT 'India' | Country of origin |
| `rating` | DECIMAL(2,1) | CHECK (1.0 to 5.0) | Vendor quality rating |

### Table: `products`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `product_id` | INT / INTEGER | PK, AUTO_INCREMENT | Unique master product ID |
| `sku` | VARCHAR(50) | NOT NULL, UNIQUE | Stock Keeping Unit code |
| `product_name`| VARCHAR(150) | NOT NULL | Commercial product name |
| `category_id` | INT / INTEGER | FK -> categories(category_id) | Parent category reference |
| `supplier_id` | INT / INTEGER | FK -> suppliers(supplier_id) | Primary vendor reference |
| `cost_price` | DECIMAL(10,2) | NOT NULL, CHECK (>= 0) | Procurement cost per unit |
| `unit_price` | DECIMAL(10,2) | NOT NULL, CHECK (>= cost_price) | Selling retail price per unit |
| `reorder_level`| INT | DEFAULT 15, CHECK (>= 0) | Minimum safe threshold |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status flag |

### Table: `warehouses`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `warehouse_id`| INT / INTEGER | PK, AUTO_INCREMENT | Unique warehouse identifier |
| `warehouse_code`| VARCHAR(30) | NOT NULL, UNIQUE | Facility code (e.g., WH-BOM-01) |
| `warehouse_name`| VARCHAR(100)| NOT NULL | Facility descriptive title |
| `location_city`| VARCHAR(80) | NOT NULL | City location of facility |
| `capacity_sqft`| INT | NOT NULL, CHECK (> 0) | Floor space capacity |
| `manager_name`| VARCHAR(100) | NULL | Lead operations supervisor |
| `is_operational`| BOOLEAN | DEFAULT TRUE | Operational status flag |

### Table: `inventory`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `inventory_id`| INT / INTEGER | PK, AUTO_INCREMENT | Surrogate inventory row ID |
| `product_id` | INT / INTEGER | FK -> products(product_id) | Product reference |
| `warehouse_id`| INT / INTEGER | FK -> warehouses(warehouse_id)| Storage location reference |
| `quantity_on_hand`| INT | NOT NULL, DEFAULT 0, CHECK (>= 0)| Available quantity |
| `bin_location`| VARCHAR(30) | DEFAULT 'A-01' | Physical rack/bin code |
| `last_restocked_at`| TIMESTAMP | NULL | Date of most recent replenishment |
| -- | Composite UK | UNIQUE(product_id, warehouse_id) | Prevents duplicate stock rows |

### Table: `customers`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | INT / INTEGER | PK, AUTO_INCREMENT | Customer identification number |
| `full_name` | VARCHAR(120) | NOT NULL | Customer legal name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE | Registered account email |
| `phone` | VARCHAR(20) | NOT NULL | Mobile number |
| `shipping_address`| TEXT | NOT NULL | Primary shipping address |
| `city` | VARCHAR(80) | NOT NULL | Delivery city |
| `customer_type`| ENUM / TEXT | DEFAULT 'Retail' | Segment (Retail/Corporate/Wholesale) |

### Table: `orders`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | INT / INTEGER | PK, AUTO_INCREMENT | Order header ID |
| `order_number`| VARCHAR(50) | NOT NULL, UNIQUE | Public order reference string |
| `customer_id` | INT / INTEGER | FK -> customers(customer_id) | Ordering party reference |
| `order_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Order submission timestamp |
| `status` | ENUM / TEXT | CHECK (Pending, Processing...) | Lifecycle order status |
| `subtotal` | DECIMAL(12,2) | CHECK (>= 0) | Pre-tax item total sum |
| `tax_amount` | DECIMAL(10,2) | CHECK (>= 0) | 18% GST calculation |
| `total_amount`| DECIMAL(12,2) | CHECK (>= 0) | Final billed amount |
| `payment_status`| ENUM / TEXT | CHECK (Unpaid, Paid, Refunded) | Payment gateway status |

### Table: `order_items`
| Column | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `order_item_id`| INT / INTEGER| PK, AUTO_INCREMENT | Line item ID |
| `order_id` | INT / INTEGER | FK -> orders(order_id) ON DELETE CASCADE | Associated order |
| `product_id` | INT / INTEGER | FK -> products(product_id) | Line item product |
| `warehouse_id`| INT / INTEGER | FK -> warehouses(warehouse_id)| Dispatched warehouse |
| `quantity` | INT | NOT NULL, CHECK (> 0) | Ordered quantity units |
| `unit_price` | DECIMAL(10,2) | NOT NULL, CHECK (> 0) | Unit price at purchase time |
| `subtotal` | DECIMAL(10,2) | NOT NULL, CHECK (> 0) | quantity * unit_price |

---

## 2. Cardinality & Relationship Breakdown

1. **Category to Product ($1 : N$):** One category holds multiple products; each product belongs to exactly one category.
2. **Supplier to Product ($1 : N$):** One vendor supplies multiple products; each product is primarily sourced from one supplier.
3. **Product to Inventory ($1 : N$) & Warehouse to Inventory ($1 : N$):** The `inventory` table forms an associative entity representing the $M : N$ relationship between Products and Warehouses with an attribute `quantity_on_hand`.
4. **Customer to Order ($1 : N$):** One customer places zero or many orders; each order belongs to one customer.
5. **Order to Order Item ($1 : N$):** One order contains one or more line items; an order item belongs to one specific order.
6. **Order to Shipment ($1 : 1$):** Each processed order maps to one fulfillment tracking record.
