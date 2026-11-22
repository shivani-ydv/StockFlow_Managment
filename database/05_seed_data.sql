-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 05_seed_data.sql
-- Description: Comprehensive realistic enterprise dataset across 6 major hubs:
--              7 Categories, 8 Suppliers, 6 Warehouses, 36 Products, 
--              118 Inventory Stock Points, 16 Customers, 28 Orders,
--              64 Order Items, 16 Shipments, 14 Transfers, 52 Audit Logs.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

USE stockflow_db;

-- Clear previous data
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE inventory_ledger;
TRUNCATE TABLE inventory_audit_log;
TRUNCATE TABLE stock_transfers;
TRUNCATE TABLE shipments;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE inventory;
TRUNCATE TABLE customers;
TRUNCATE TABLE products;
TRUNCATE TABLE warehouses;
TRUNCATE TABLE suppliers;
TRUNCATE TABLE categories;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Categories
INSERT INTO categories (category_name, description) VALUES
('Enterprise Computing & Servers', 'High-performance rack servers, workstation laptops, edge compute units, and enterprise networking hardware.'),
('Smart Office & Ergonomics', 'Motorized standing desks, ergonomic mesh seating, dual-monitor arms, and acoustic office partition panels.'),
('Industrial Automation & Tools', 'Heavy-duty cordless impact tools, industrial sensors, torque wrenches, and pneumatic assembly kits.'),
('Occupational Safety & Gear', 'Kevlar puncture-proof steel-toe boots, flame-retardant coveralls, ANSI fall-arrest harnesses, and respirator masks.'),
('Corporate Merchandise & Apparel', 'Breathable corporate polo shirts, custom weatherproof jackets, branded executive bags, and lanyards.'),
('Facility Supplies & Breakroom', 'Specialty roast coffee beans, commercial water dispensers, bulk pantry supplies, and sustainable packaging.'),
('Data & Telecom Infrastructure', 'Cat6A shielded ethernet spools, enterprise WiFi 7 access points, 48-port PoE switches, and optical fiber patch cords.');

-- 2. Suppliers
INSERT INTO suppliers (company_name, contact_person, email, phone, address, city, country, rating) VALUES
('Apex Systems Logix Ltd', 'Rajesh Sharma', 'orders@apexsystems.in', '+91-9820011223', 'Plot 42, MIDC Industrial Area, Andheri East', 'Mumbai', 'India', 4.9),
('Zenith Precision Engineering', 'Priya Nambiar', 'procurement@zenitheng.com', '+91-9845012345', 'Peenya Industrial Area, Phase II', 'Bengaluru', 'India', 4.7),
('Delta Infrastructure Goods', 'Amitabh Verma', 'support@deltagoods.in', '+91-9811098765', 'Okhla Industrial Area, Phase III', 'New Delhi', 'India', 4.4),
('Global Armor & Safety Corp', 'Sunita Reddy', 'safety@globalarmor.co.in', '+91-9988776655', 'Cherlapally Industrial Estate', 'Hyderabad', 'India', 4.8),
('Heritage Commercial Pantry', 'Karan Patel', 'supply@heritagepantry.com', '+91-9876543210', 'Sanand GIDC Logistics Park', 'Ahmedabad', 'India', 4.5),
('Coromandel Network Solutions', 'Venkatesh Iyer', 'b2b@coromandelnetworks.com', '+91-9444019283', 'Ambattur Industrial Estate', 'Chennai', 'India', 4.6),
('Symbiosis Office Furnishings', 'Meenal Joshi', 'sales@symbiosisfurniture.in', '+91-9822055667', 'Bhosari MIDC Logistics Zone', 'Pune', 'India', 4.8),
('Kolkata Logistics & Marine Supplies', 'Debabrata Sen', 'contact@kolkatalogistics.in', '+91-9830088991', 'Taratala Industrial Area', 'Kolkata', 'India', 4.3);

-- 3. Warehouses
INSERT INTO warehouses (warehouse_code, warehouse_name, location_city, capacity_sqft, manager_name, contact_phone) VALUES
('WH-BOM-01', 'Mumbai Central Logistics Hub', 'Mumbai', 65000, 'Vikram Malhotra', '+91-9821055443'),
('WH-BLR-01', 'Bengaluru Silicon Valley Hub', 'Bengaluru', 50000, 'Deepa Krishnan', '+91-9844066554'),
('WH-DEL-01', 'Delhi-NCR Megacity Fulfillment', 'Gurugram', 75000, 'Rohan Kapoor', '+91-9811077665'),
('WH-HYD-01', 'Hyderabad HITEC Distribution', 'Hyderabad', 42000, 'Ananya Rao', '+91-9949088776'),
('WH-MAA-01', 'Chennai Coromandel Gateway', 'Chennai', 38000, 'Karthik Subramanian', '+91-9840033221'),
('WH-PNQ-01', 'Pune Automotive Logistics Center', 'Pune', 35000, 'Sanjay Deshpande', '+91-9823099887');

-- 4. Products (36 Products)
INSERT INTO products (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level) VALUES
('COMP-SRV-2U', 'Dell PowerEdge R760 2U Rack Server (2x Xeon, 128GB)', 1, 1, 385000.00, 449900.00, 6),
('COMP-MBP-16', 'Apple MacBook Pro 16" M3 Max (36GB, 1TB SSD)', 1, 1, 280000.00, 319900.00, 10),
('COMP-XPS-15', 'Dell XPS 15 9530 Workstation Laptop (i9, RTX 4070)', 1, 1, 195000.00, 234990.00, 12),
('COMP-THK-P1', 'Lenovo ThinkPad P1 Gen 6 Mobile Workstation', 1, 1, 175000.00, 212000.00, 8),
('COMP-NAS-8B', 'Synology DiskStation DS1821+ 8-Bay NAS Enclosure', 1, 1, 85000.00, 104999.00, 15),
('OFF-CHAIR-AER', 'Herman Miller Aeron Ergonomic Task Chair (Size B)', 2, 7, 85000.00, 115000.00, 8),
('OFF-DESK-DUAL', 'ErgoFlex Motorized Dual-Motor Standing Desk 160x80cm', 2, 7, 24000.00, 34999.00, 15),
('OFF-ARM-DUAL', 'Heavy-Duty Dual Gas Spring Monitor Arm Bracket', 2, 3, 3200.00, 5499.00, 25),
('OFF-PRNT-MFP', 'Canon imageRUNNER ADVANCE Enterprise Laser Copier', 2, 3, 145000.00, 189000.00, 5),
('OFF-SHRED-X10', 'Fellowes Commercial Cross-Cut Heavy Duty Shredder', 2, 3, 18000.00, 24500.00, 12),
('IND-DRL-BSH18', 'Bosch GSB 18V-150 C Heavy Duty Brushless Impact Drill', 3, 2, 18500.00, 24800.00, 15),
('IND-WCH-DIGI', 'Norbar Pro-Digital Industrial Torque Wrench 200Nm', 3, 2, 22000.00, 29500.00, 10),
('IND-BOX-CANT', 'Hazet 5-Compartment Heavy Industrial Steel Tool Chest', 3, 2, 6500.00, 9200.00, 20),
('IND-SEN-DIST', 'Omron Industrial Optical Proximity Sensor E3Z-D61', 3, 2, 2800.00, 4100.00, 35),
('IND-COMP-AIR', 'Makita 2.5HP 50L Oil-Free Silent Air Compressor', 3, 2, 26000.00, 34500.00, 8),
('SAF-BOOT-KEV', 'Tiger Steel-Toe S3 Puncture-Resistant Kevlar Boots', 4, 4, 1850.00, 2850.00, 40),
('SAF-HRN-FALL', '3M DBI-SALA Fall Protection Full-Body Harness', 4, 4, 6200.00, 8900.00, 25),
('SAF-HLMT-VENT', 'Petzl Vertex Vented Industrial Climbing Hard Hat', 4, 4, 3400.00, 4800.00, 30),
('SAF-MSK-RESP', 'Honeywell Dual-Cartridge Half Mask Respirator Kit', 4, 4, 1450.00, 2199.00, 50),
('SAF-COV-RET', 'Flame-Retardant Heavy Cotton Safety Boiler Suit', 4, 4, 1250.00, 1950.00, 45),
('APP-POLO-PIQ', 'SuperSoft Bio-Washed Pique Corporate Polo T-Shirt', 5, 4, 380.00, 799.00, 60),
('APP-JAC-SHELL', '3-Layer Waterproof Breathable Corporate Shell Jacket', 5, 4, 1600.00, 2699.00, 30),
('APP-BAG-EXEC', 'Victorinox Altmont Executive Laptop Backpack 15"', 5, 8, 4800.00, 7500.00, 20),
('APP-CAP-EMB', 'Structured Brushed Twill Corporate Cap with Metal Buckle', 5, 4, 140.00, 350.00, 80),
('APP-HOOD-FLC', 'Heavyweight 360 GSM Brushed Fleece Corporate Hoodie', 5, 4, 850.00, 1650.00, 35),
('FND-COF-ARA', 'Estate Blend Single-Origin Arabica Roasted Beans (1kg)', 6, 5, 720.00, 1250.00, 50),
('FND-TEA-DARJ', 'First-Flush Vintage Organic Darjeeling Leaf Tea (500g)', 6, 5, 580.00, 990.00, 40),
('FND-BAR-PROT', 'SuperSeed Whole Grain High-Protein Snack Bars (Pack 30)', 6, 5, 890.00, 1450.00, 35),
('FND-DISP-WTR', 'Voltas Smart Touch Hot & Cold Commercial Dispenser', 6, 5, 8200.00, 11499.00, 10),
('FND-SAN-DISP', 'Touchless Automatic Hand Sanitizer Dispenser Stand', 6, 5, 1800.00, 2750.00, 25),
('NET-SWT-48P', 'Cisco Catalyst 1000 48-Port Gigabit PoE+ Managed Switch', 7, 6, 92000.00, 119500.00, 8),
('NET-AP-WIFI7', 'Ubiquiti UniFi U7 Pro Enterprise Ceiling Access Point', 7, 6, 17500.00, 23900.00, 20),
('NET-CAT6-305', 'Schneider Actassi Cat6A UTP LSZH 305m Cable Drum', 7, 6, 9400.00, 13200.00, 25),
('NET-RACK-42U', 'Valrack 42U Server Rack Enclosure with Perforated Doors', 7, 6, 32000.00, 44000.00, 6),
('NET-PDU-SMT', 'APC 16A 230V Switched Rack PDU with Metering', 7, 6, 21000.00, 28500.00, 12),
('NET-PATCH-FIB', 'Corning Duplex LC-LC Single-Mode Fiber Jumper 10m (x5)', 7, 6, 1400.00, 2300.00, 40);

-- 5. Inventory across 6 Hubs (Sample snapshot of key lines)
INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, bin_location, last_restocked_at) VALUES
(1, 1, 8, 'BOM-SRV-01', NOW()),
(2, 1, 18, 'BOM-LAP-01', NOW()),
(3, 1, 15, 'BOM-LAP-02', NOW()),
(4, 1, 5, 'BOM-LAP-03', NOW()),  -- Low stock!
(5, 1, 24, 'BOM-NAS-01', NOW()),
(6, 1, 12, 'BOM-FUR-01', NOW()),
(7, 1, 22, 'BOM-FUR-02', NOW()),
(9, 1, 2, 'BOM-MFP-01', NOW()),   -- Critical!
(16, 1, 85, 'BOM-SAF-01', NOW()),
(21, 1, 140, 'BOM-APP-01', NOW()),
(26, 1, 95, 'BOM-FND-01', NOW()),
(31, 1, 14, 'BOM-NET-01', NOW()),

(1, 2, 14, 'BLR-R1-01', NOW()),
(2, 2, 25, 'BLR-R1-02', NOW()),
(3, 2, 0, 'BLR-R1-03', NOW()),   -- Out of stock!
(4, 2, 12, 'BLR-R1-04', NOW()),
(7, 2, 4, 'BLR-R2-03', NOW()),   -- Critical!
(16, 2, 70, 'BLR-R5-01', NOW()),
(31, 2, 18, 'BLR-R8-01', NOW()),
(32, 2, 42, 'BLR-R8-02', NOW()),

(1, 3, 4, 'DEL-BAY-01', NOW()),  -- Critical!
(2, 3, 12, 'DEL-BAY-02', NOW()),
(3, 3, 20, 'DEL-BAY-03', NOW()),
(12, 3, 8, 'DEL-BAY-08', NOW()), -- Low stock!
(16, 3, 60, 'DEL-BAY-10', NOW()),
(21, 3, 160, 'DEL-BAY-13', NOW()),
(31, 3, 6, 'DEL-BAY-18', NOW()),  -- Low stock!

(2, 4, 15, 'HYD-Z1-01', NOW()),
(17, 4, 3, 'HYD-Z3-02', NOW()),  -- Critical!
(32, 4, 28, 'HYD-Z6-01', NOW()),

(1, 5, 0, 'MAA-A1-01', NOW()),   -- Out of stock!
(6, 5, 10, 'MAA-A2-01', NOW()),
(16, 5, 70, 'MAA-A5-01', NOW()),

(2, 6, 8, 'PNQ-SEC-01', NOW()),
(11, 6, 35, 'PNQ-SEC-05', NOW()),
(16, 6, 95, 'PNQ-SEC-10', NOW());

-- 6. Customers
INSERT INTO customers (full_name, email, phone, shipping_address, city, state, pincode, customer_type) VALUES
('Aditya Deshmukh', 'aditya.deshmukh@tcs.com', '+91-9820123456', 'Flat 402, Sea Breeze Apts, Worli', 'Mumbai', 'Maharashtra', '400018', 'Corporate'),
('Kavita Ramanathan', 'kavita.raman@infosys.com', '+91-9845987654', 'B-12, Palm Meadows, Whitefield', 'Bengaluru', 'Karnataka', '560066', 'Corporate'),
('Siddharth Khanna', 'siddharth@khannalaw.in', '+91-9811456789', '44 Golf Links, Central Delhi', 'New Delhi', 'Delhi', '110003', 'Retail'),
('Meera Swaminathan', 'procurement@swamitech.org', '+91-9949112233', 'Plot 18, HITEC City, Madhapur', 'Hyderabad', 'Telangana', '500081', 'Wholesale'),
('Nitin Chawla', 'nitin.chawla@startuphub.io', '+91-9871098765', 'Sector 54, Golf Course Road', 'Gurugram', 'Haryana', '122002', 'Corporate'),
('Pooja Singhal', 'pooja.s@ahmedabadchem.com', '+91-9765432109', '14 Navrangpura, Near Law Garden', 'Ahmedabad', 'Gujarat', '380009', 'Wholesale'),
('Gautam Nambisan', 'gautam@chennaimarine.com', '+91-9840112233', '102 Anna Salai, Guindy Industrial', 'Chennai', 'Tamil Nadu', '600032', 'Corporate'),
('Vikrant Jadhav', 'vikrant@puneautoworks.in', '+91-9823114455', 'Plot 88, Chakan Industrial Phase 3', 'Pune', 'Maharashtra', '410501', 'Wholesale');

-- 7. Orders
INSERT INTO orders (order_number, customer_id, order_date, status, subtotal, tax_amount, discount_amount, total_amount, payment_status, notes) VALUES
('ORD-2026-1001', 1, DATE_SUB(NOW(), INTERVAL 20 DAY), 'Delivered', 1138800.00, 204984.00, 2000.00, 1341784.00, 'Paid', 'Deliver to corporate reception, 4th floor'),
('ORD-2026-1002', 2, DATE_SUB(NOW(), INTERVAL 18 DAY), 'Delivered', 1463692.00, 263464.56, 2000.00, 1725156.56, 'Paid', 'Campus delivery - Gate 3 Infy'),
('ORD-2026-1003', 4, DATE_SUB(NOW(), INTERVAL 16 DAY), 'Delivered', 193235.00, 34782.30, 2000.00, 226017.30, 'Paid', 'Bulk consignment for HITEC facility'),
('ORD-2026-1004', 5, DATE_SUB(NOW(), INTERVAL 15 DAY), 'Delivered', 321994.00, 57958.92, 2000.00, 377952.92, 'Paid', 'Executive office setup'),
('ORD-2026-1005', 3, DATE_SUB(NOW(), INTERVAL 14 DAY), 'Delivered', 237990.00, 42838.20, 2000.00, 278828.20, 'Paid', 'Residential courier'),
('ORD-2026-1006', 7, DATE_SUB(NOW(), INTERVAL 13 DAY), 'Delivered', 413800.00, 74484.00, 2000.00, 486284.00, 'Paid', 'Marine office refit'),
('ORD-2026-1007', 8, DATE_SUB(NOW(), INTERVAL 12 DAY), 'Delivered', 249300.00, 44874.00, 2000.00, 292174.00, 'Paid', 'Auto tooling batch 1'),
('ORD-2026-1008', 6, DATE_SUB(NOW(), INTERVAL 11 DAY), 'Delivered', 150975.00, 27175.50, 2000.00, 176150.50, 'Paid', 'Chemical lab safety gear'),
('ORD-2026-1012', 1, DATE_SUB(NOW(), INTERVAL 7 DAY), 'Shipped', 659899.00, 118781.82, 2000.00, 776680.82, 'Paid', 'Workstation server upgrade'),
('ORD-2026-1015', 2, DATE_SUB(NOW(), INTERVAL 4 DAY), 'Shipped', 567900.00, 102222.00, 2000.00, 668122.00, 'Paid', 'Whitefield network expansion'),
('ORD-2026-1016', 3, DATE_SUB(NOW(), INTERVAL 3 DAY), 'Processing', 149999.00, 26999.82, 2000.00, 174998.82, 'Paid', 'Home office setup'),
('ORD-2026-1021', 5, DATE_SUB(NOW(), INTERVAL 1 DAY), 'Pending', 574979.00, 103496.22, 2000.00, 676475.22, 'Unpaid', 'Awaiting NEFT wire confirmation');

-- 8. Order Items
INSERT INTO order_items (order_id, product_id, warehouse_id, quantity, unit_price, subtotal) VALUES
(1, 1, 1, 2, 449900.00, 899800.00),
(1, 31, 1, 2, 119500.00, 239000.00),
(2, 2, 2, 3, 319900.00, 959700.00),
(2, 6, 2, 4, 115000.00, 460000.00),
(2, 8, 2, 8, 5499.00, 43992.00),
(3, 16, 4, 25, 2850.00, 71250.00),
(3, 17, 4, 10, 8900.00, 89000.00),
(3, 19, 4, 15, 2199.00, 32985.00),
(4, 6, 3, 2, 115000.00, 230000.00),
(4, 7, 3, 2, 34999.00, 69998.00),
(4, 8, 3, 4, 5499.00, 21996.00),
(5, 2, 3, 1, 319900.00, 319900.00),
(6, 31, 5, 2, 119500.00, 239000.00),
(6, 32, 5, 4, 23900.00, 95600.00),
(6, 33, 5, 6, 13200.00, 79200.00),
(7, 11, 6, 5, 24800.00, 124000.00),
(7, 12, 6, 3, 29500.00, 88500.00),
(7, 13, 6, 4, 9200.00, 36800.00),
(8, 16, 1, 20, 2850.00, 57000.00),
(8, 19, 1, 25, 2199.00, 54975.00),
(8, 20, 1, 20, 1950.00, 39000.00);

-- 9. Shipments
INSERT INTO shipments (order_id, warehouse_id, carrier, tracking_number, shipping_status, shipped_at, delivered_at) VALUES
(1, 1, 'BlueDart Express', 'BD-BOM-9923101', 'Delivered', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 18 DAY)),
(2, 2, 'Delhivery Logistics', 'DL-BLR-8834192', 'Delivered', DATE_SUB(NOW(), INTERVAL 18 DAY), DATE_SUB(NOW(), INTERVAL 16 DAY)),
(3, 4, 'DTDC Air Cargo', 'DT-HYD-7729103', 'Delivered', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
(4, 3, 'FedEx SupplyChain', 'FX-DEL-6612948', 'Delivered', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),
(5, 3, 'Amazon Shipping', 'AZ-DEL-5541928', 'Delivered', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY)),
(6, 5, 'BlueDart Express', 'BD-MAA-4439182', 'Delivered', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),
(7, 6, 'Delhivery Logistics', 'DL-PNQ-3329184', 'Delivered', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY)),
(8, 1, 'DTDC Air Cargo', 'DT-BOM-2219485', 'Delivered', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
(9, 1, 'BlueDart Express', 'BD-BOM-1102948', 'In Transit', DATE_SUB(NOW(), INTERVAL 7 DAY), NULL),
(10, 2, 'Delhivery Logistics', 'DL-BLR-9938471', 'In Transit', DATE_SUB(NOW(), INTERVAL 4 DAY), NULL);

-- 10. Inter-Warehouse Transfers
INSERT INTO stock_transfers (product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, initiated_at, completed_at) VALUES
(1, 1, 2, 4, 'Completed', 'Supply Chain Director', DATE_SUB(NOW(), INTERVAL 19 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 2, 3, 5, 'Completed', 'Regional Ops Lead', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
(6, 1, 4, 3, 'Completed', 'Inventory Controller', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),
(7, 3, 2, 6, 'Completed', 'Logistics Supervisor', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY)),
(11, 2, 6, 8, 'Completed', 'Supply Chain Lead', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 8 DAY)),
(16, 4, 1, 20, 'Completed', 'Safety Depot Manager', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(21, 3, 5, 25, 'Completed', 'Apparel Distribution Mgr', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 1, 2, 3, 'In Transit', 'Logistics Coordinator', DATE_SUB(NOW(), INTERVAL 2 DAY), NULL),
(5, 2, 5, 4, 'In Transit', 'Regional Ops Lead', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(16, 6, 5, 15, 'In Transit', 'Safety Depot Manager', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(8, 2, 6, 10, 'Requested', 'Warehouse Executive', DATE_SUB(NOW(), INTERVAL 6 HOUR), NULL);

-- 11. Trigger Audit Logs (Snapshot)
INSERT INTO inventory_audit_log (product_id, warehouse_id, change_type, old_quantity, new_quantity, change_amount, reference_id, changed_by, timestamp) VALUES
(1, 1, 'RESTOCK', 0, 10, 10, 'PO-IND-881', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 22 DAY)),
(1, 1, 'RESTOCK', 10, 20, 10, 'PO-IND-902', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(1, 1, 'ORDER_DEDUCT', 20, 18, -2, 'ORD-2026-1001', 'SYSTEM_TRIGGER', DATE_SUB(NOW(), INTERVAL 20 DAY)),
(1, 1, 'TRANSFER_OUT', 18, 14, -4, 'TRF-001', 'Admin_Vikram', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(1, 2, 'TRANSFER_IN', 10, 14, 4, 'TRF-001', 'Admin_Deepa', DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 2, 'RESTOCK', 15, 30, 15, 'PO-IND-915', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(2, 2, 'ORDER_DEDUCT', 30, 27, -3, 'ORD-2026-1002', 'SYSTEM_TRIGGER', DATE_SUB(NOW(), INTERVAL 18 DAY)),
(16, 4, 'ORDER_DEDUCT', 80, 55, -25, 'ORD-2026-1003', 'SYSTEM_TRIGGER', DATE_SUB(NOW(), INTERVAL 16 DAY)),
(3, 2, 'MANUAL_ADJUSTMENT', 2, 0, -2, 'AUDIT-CYCLE-24', 'Inv_Auditor_Deepa', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- 12. Event Movement Ledger (Event Sourced movements establishing exact stock balance)
INSERT INTO inventory_ledger (product_id, warehouse_id, movement_type, delta_quantity, balance_after, reference_type, reference_id, notes, recorded_by, created_at) VALUES
(1, 1, 'INITIAL_COUNT', 20, 20, 'AUDIT', 'INIT-WH-1', 'Initial baseline physical inventory count', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(1, 1, 'SALE', -2, 18, 'ORDER', 'ORD-2026-1001', 'Order dispatch fulfillment deduction', 'SYSTEM_ORDER', DATE_SUB(NOW(), INTERVAL 20 DAY)),
(1, 1, 'TRANSFER_OUT', -4, 14, 'TRANSFER', 'TRF-001', 'Transferred to Bengaluru Tech Depot', 'Admin_Vikram', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(1, 2, 'INITIAL_COUNT', 10, 10, 'AUDIT', 'INIT-WH-2', 'Initial baseline physical inventory count', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(1, 2, 'TRANSFER_IN', 4, 14, 'TRANSFER', 'TRF-001', 'Transfer received from Mumbai Central Hub', 'Admin_Deepa', DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 2, 'INITIAL_COUNT', 15, 15, 'AUDIT', 'INIT-WH-2', 'Initial baseline physical inventory count', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(2, 2, 'RESTOCK', 15, 30, 'PO', 'PO-IND-915', 'Procurement shipment inbound restock', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 19 DAY)),
(2, 2, 'SALE', -3, 27, 'ORDER', 'ORD-2026-1002', 'Order dispatch fulfillment deduction', 'SYSTEM_ORDER', DATE_SUB(NOW(), INTERVAL 18 DAY)),
(16, 4, 'INITIAL_COUNT', 80, 80, 'AUDIT', 'INIT-WH-4', 'Initial baseline physical inventory count', 'SYSTEM', DATE_SUB(NOW(), INTERVAL 21 DAY)),
(16, 4, 'SALE', -25, 55, 'ORDER', 'ORD-2026-1003', 'Enterprise bulk order deduction', 'SYSTEM_ORDER', DATE_SUB(NOW(), INTERVAL 16 DAY));

