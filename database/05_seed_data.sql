-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 05_seed_data.sql
-- Description: Realistic initial sample data representing real-world inventory,
--              multi-warehouse distribution, orders, and shipments.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

USE stockflow_db;

-- 1. Categories
INSERT INTO categories (category_name, description) VALUES
('Consumer Electronics', 'Smartphones, laptops, tablets, audio accessories, and peripherals'),
('Office Equipment', 'Printers, ergonomic furniture, paper goods, and stationery'),
('Industrial Supplies', 'Power tools, safety gear, fasteners, and storage racks'),
('Apparel & Footwear', 'Work uniforms, safety boots, and branded corporate merchandise'),
('Packaged Foods & Beverages', 'Non-perishable snack packs, bottled beverages, and pantry items');

-- 2. Suppliers
INSERT INTO suppliers (company_name, contact_person, email, phone, address, city, country, rating) VALUES
('Apex Tech Logix Ltd', 'Rajesh Sharma', 'orders@apextech.in', '+91-9820011223', 'Plot 42, MIDC Industrial Area, Andheri East', 'Mumbai', 'India', 4.8),
('Zenith Industrial Tools', 'Priya Nambiar', 'sales@zenithtools.com', '+91-9845012345', 'Peenya Industrial Area, Phase II', 'Bengaluru', 'India', 4.5),
('Delta Office Corp', 'Amitabh Verma', 'support@deltaoffice.in', '+91-9811098765', 'Okhla Industrial Area, Phase III', 'New Delhi', 'India', 4.2),
('Global Wear Innovations', 'Sunita Reddy', 'contact@globalwear.co.in', '+91-9988776655', 'Cherlapally Industrial Estate', 'Hyderabad', 'India', 4.6),
('Heritage Refreshments', 'Karan Patel', 'supply@heritagerefresh.com', '+91-9876543210', 'Sanand GIDC', 'Ahmedabad', 'India', 4.4);

-- 3. Warehouses
INSERT INTO warehouses (warehouse_code, warehouse_name, location_city, capacity_sqft, manager_name, contact_phone) VALUES
('WH-BOM-01', 'Mumbai Central Logistics Hub', 'Mumbai', 45000, 'Vikram Malhotra', '+91-9821055443'),
('WH-BLR-01', 'Bengaluru Tech Park Warehouse', 'Bengaluru', 38000, 'Deepa Krishnan', '+91-9844066554'),
('WH-DEL-01', 'Delhi-NCR Distribution Center', 'Gurugram', 50000, 'Rohan Kapoor', '+91-9811077665'),
('WH-HYD-01', 'Hyderabad South Fulfillment Center', 'Hyderabad', 30000, 'Ananya Rao', '+91-9949088776');

-- 4. Products (15 diverse products)
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

-- 5. Inventory across 4 Warehouses
-- Intentionally creating normal stock, low stock, and out of stock to test alerts!
INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, bin_location, last_restocked_at) VALUES
-- Mumbai Hub
(1, 1, 18, 'A-01-01', NOW()),
(2, 1, 5,  'A-01-02', NOW()), -- Low stock! (reorder is 8)
(3, 1, 32, 'A-02-01', NOW()),
(4, 1, 60, 'A-02-02', NOW()),
(5, 1, 20, 'B-01-01', NOW()),
(8, 1, 14, 'C-01-01', NOW()),
(13, 1, 80, 'D-01-01', NOW()),

-- Bengaluru Hub
(1, 2, 12, 'BLR-E1', NOW()),
(2, 2, 0,  'BLR-E2', NOW()), -- Out of stock!
(3, 2, 15, 'BLR-E3', NOW()), -- Low stock! (reorder is 20)
(4, 2, 45, 'BLR-E4', NOW()),
(6, 2, 9,  'BLR-F1', NOW()),
(7, 2, 14, 'BLR-F2', NOW()),
(9, 2, 55, 'BLR-G1', NOW()),
(12, 2, 120, 'BLR-H1', NOW()),

-- Delhi Hub
(1, 3, 8,  'DEL-A1', NOW()),  -- Low stock! (reorder is 10)
(5, 3, 25, 'DEL-B1', NOW()),
(6, 3, 4,  'DEL-B2', NOW()),  -- Low stock! (reorder is 6)
(7, 3, 18, 'DEL-B3', NOW()),
(8, 3, 22, 'DEL-C1', NOW()),
(10, 3, 40, 'DEL-C2', NOW()),
(11, 3, 35, 'DEL-D1', NOW()),

-- Hyderabad Hub
(3, 4, 18, 'HYD-01', NOW()),
(4, 4, 30, 'HYD-02', NOW()),
(9, 4, 28, 'HYD-03', NOW()), -- Low stock (reorder is 30)
(13, 4, 50, 'HYD-04', NOW()),
(14, 4, 60, 'HYD-05', NOW()),
(15, 4, 45, 'HYD-06', NOW());

-- 6. Customers
INSERT INTO customers (full_name, email, phone, shipping_address, city, state, pincode, customer_type) VALUES
('Aditya Deshmukh', 'aditya.deshmukh@gmail.com', '+91-9820123456', 'Flat 402, Sea Breeze Apts, Worli', 'Mumbai', 'Maharashtra', '400018', 'Retail'),
('Kavita Raman', 'kavita.raman@infosys.com', '+91-9845987654', 'B-12, Palm Meadows, Whitefield', 'Bengaluru', 'Karnataka', '560066', 'Corporate'),
('Siddharth Khanna', 'siddharth@khannalaw.in', '+91-9811456789', '44 Golf Links, Central Delhi', 'New Delhi', 'Delhi', '110003', 'Retail'),
('Meera Swaminathan', 'procurement@swamitech.org', '+91-9949112233', 'Plot 18, HITEC City, Madhapur', 'Hyderabad', 'Telangana', '500081', 'Wholesale'),
('Nitin Chawla', 'nitin.chawla@startuphub.io', '+91-9871098765', 'Sector 54, Golf Course Road', 'Gurugram', 'Haryana', '122002', 'Corporate'),
('Pooja Singhal', 'pooja.s@gmail.com', '+91-9765432109', '14 Navrangpura, Near Law Garden', 'Ahmedabad', 'Gujarat', '380009', 'Retail');

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

-- 11. Inventory Audit Log
INSERT INTO inventory_audit_log (product_id, warehouse_id, change_type, old_quantity, new_quantity, change_amount, reference_id, changed_by) VALUES
(1, 1, 'RESTOCK', 10, 20, 10, 'PO-2026-101', 'SYSTEM'),
(1, 1, 'ORDER_DEDUCT', 20, 19, -1, 'ORD-2026-001', 'SYSTEM'),
(1, 1, 'TRANSFER_OUT', 19, 16, -3, 'TRF-001', 'Admin_Vikram'),
(1, 2, 'TRANSFER_IN', 9, 12, 3, 'TRF-001', 'Admin_Deepa'),
(2, 2, 'ORDER_DEDUCT', 2, 0, -2, 'ORD-LEGACY', 'SYSTEM');
