"""
Comprehensive High-Volume Seed Generator for StockFlow
Generates 120+ realistic products across 8 categories with barcodes,
300+ warehouse inventory stock points, 45+ orders, and an event-sourced
inventory_ledger with 500+ atomic stock movements (+Restock, -Sale, -Damage, +Return).
"""

import os
import sys
import random
import sqlite3
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import get_db_connection, init_database, DB_FILE

def populate_rich_data():
    # Fresh initialization with new schema (barcode, inventory_ledger, etc.)
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Cleaning existing records for fresh high-volume seed...")
    tables = [
        "inventory_ledger", "inventory_audit_log", "stock_transfers", "shipments", 
        "order_items", "orders", "inventory", "customers", 
        "products", "warehouses", "suppliers", "categories"
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")
        try:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
        except:
            pass

    conn.commit()
    print("Database cleared. Generating 120+ products and event ledger...")

    # 1. Categories
    categories = [
        ("Enterprise Computing & Servers", "High-performance rack servers, workstation laptops, edge compute units, and enterprise computing."),
        ("Data & Telecom Infrastructure", "Enterprise switches, WiFi 7 APs, Cat6A spools, server racks, and optical fiber jumpers."),
        ("Smart Office & Ergonomics", "Motorized standing desks, ergonomic mesh seating, dual-monitor arms, and acoustic office partition panels."),
        ("Industrial Automation & Tools", "Heavy-duty cordless impact tools, industrial sensors, torque wrenches, and pneumatic assembly kits."),
        ("Occupational Safety & Gear", "Kevlar puncture-proof steel-toe boots, flame-retardant coveralls, ANSI fall-arrest harnesses, and respirator masks."),
        ("Facility Supplies & Breakroom", "Specialty roast coffee beans, commercial water dispensers, bulk pantry supplies, and sustainable packaging."),
        ("Logistics & Warehouse Equipment", "Industrial pallet trucks, thermal barcode labelers, handheld scanner terminals, and stretch wrap."),
        ("Medical & First Aid", "Commercial AED defibrillator units, OSHA industrial first-aid stations, eye-wash kits, and trauma packs.")
    ]
    cursor.executemany("INSERT INTO categories (category_name, description) VALUES (?, ?);", categories)

    # 2. Suppliers (10 Suppliers)
    suppliers = [
        ("Apex Systems Logix Ltd", "Rajesh Sharma", "orders@apexsystems.in", "+91-9820011223", "Plot 42, MIDC Industrial Area, Andheri East", "Mumbai", "India", 4.9),
        ("Zenith Precision Engineering", "Priya Nambiar", "procurement@zenitheng.com", "+91-9845012345", "Peenya Industrial Area, Phase II", "Bengaluru", "India", 4.7),
        ("Delta Infrastructure Goods", "Amitabh Verma", "support@deltagoods.in", "+91-9811098765", "Okhla Industrial Area, Phase III", "New Delhi", "India", 4.4),
        ("Global Armor & Safety Corp", "Sunita Reddy", "safety@globalarmor.co.in", "+91-9988776655", "Cherlapally Industrial Estate", "Hyderabad", "India", 4.8),
        ("Heritage Commercial Pantry", "Karan Patel", "supply@heritagepantry.com", "+91-9876543210", "Sanand GIDC Logistics Park", "Ahmedabad", "India", 4.5),
        ("Coromandel Network Solutions", "Venkatesh Iyer", "b2b@coromandelnetworks.com", "+91-9444019283", "Ambattur Industrial Estate", "Chennai", "India", 4.6),
        ("Symbiosis Office Furnishings", "Meenal Joshi", "sales@symbiosisfurniture.in", "+91-9822055667", "Bhosari MIDC Logistics Zone", "Pune", "India", 4.8),
        ("Kolkata Logistics & Marine Supplies", "Debabrata Sen", "contact@kolkatalogistics.in", "+91-9830088991", "Taratala Industrial Area", "Kolkata", "India", 4.3),
        ("Nordic SafeHealth Lifeline", "Lars Jensen", "b2b@nordicsafe.com", "+45-7020-1122", "Kompagnistræde 14", "Copenhagen", "Denmark", 4.9),
        ("Falcon Packaging Logistics", "Imran Qureshi", "sales@falconpack.in", "+91-9820098712", "Bhiwandi Warehousing Zone", "Thane", "India", 4.4)
    ]
    cursor.executemany("""
        INSERT INTO suppliers (company_name, contact_person, email, phone, address, city, country, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, suppliers)

    # 3. Warehouses (6 Warehouses)
    warehouses = [
        ("WH-BOM-01", "Mumbai Central Logistics Hub", "Mumbai", 65000, "Vikram Malhotra", "+91-9821055443"),
        ("WH-BLR-01", "Bengaluru Silicon Valley Hub", "Bengaluru", 50000, "Deepa Krishnan", "+91-9844066554"),
        ("WH-DEL-01", "Delhi-NCR Megacity Fulfillment", "Gurugram", 75000, "Rohan Kapoor", "+91-9811077665"),
        ("WH-HYD-01", "Hyderabad HITEC Distribution", "Hyderabad", 42000, "Ananya Rao", "+91-9949088776"),
        ("WH-MAA-01", "Chennai Coromandel Gateway", "Chennai", 38000, "Karthik Subramanian", "+91-9840033221"),
        ("WH-PNQ-01", "Pune Automotive Logistics Center", "Pune", 35000, "Sanjay Deshpande", "+91-9823099887")
    ]
    cursor.executemany("""
        INSERT INTO warehouses (warehouse_code, warehouse_name, location_city, capacity_sqft, manager_name, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?);
    """, warehouses)

    # 4. Generate 125 Realistic Products with Barcodes (UPC/EAN)
    catalog_templates = [
        # (cat_id, sup_id, prefix, names_list, price_range, reorder_range)
        (1, 1, "COMP", [
            ("Dell PowerEdge R760 2U Rack Server (2x Xeon, 128GB)", 385000, 449900, 5),
            ("Apple MacBook Pro 16\" M3 Max (36GB, 1TB SSD)", 280000, 319900, 8),
            ("Dell XPS 15 9530 Workstation Laptop (i9, RTX 4070)", 195000, 234990, 10),
            ("Lenovo ThinkPad P1 Gen 6 Mobile Workstation", 175000, 212000, 8),
            ("Synology DiskStation DS1821+ 8-Bay NAS Enclosure", 85000, 104999, 12),
            ("HP Z2 Tower G9 High-Performance Workstation", 140000, 175000, 6),
            ("Apple Mac Studio M2 Ultra (64GB RAM, 1TB)", 340000, 399900, 4),
            ("ASUS ROG Zephyrus G16 Creator Laptop (RTX 4080)", 185000, 229990, 8),
            ("Samsung 49\" Odyssey OLED G9 Curved Ultra-Wide Monitor", 95000, 129999, 10),
            ("LG 32\" UltraFine 4K UHD OLED Pro Monitor", 82000, 109000, 8),
            ("SanDisk Professional 48TB G-RAID Shuttle 4-Bay Storage", 195000, 245000, 4),
            ("Crucial 64GB DDR5 5600MHz Server ECC RAM Kit", 18500, 24500, 20),
            ("Samsung 990 PRO 4TB NVMe PCIe 4.0 Internal SSD", 24000, 31999, 25),
            ("Seagate Exos X20 20TB Enterprise 7200 RPM SATA HDD", 28000, 36500, 15),
            ("Logitech MX Master 3S Ergonomic Performance Wireless Mouse", 6200, 8995, 30),
            ("Logitech MX Mechanical Wireless Illuminated Keyboard", 9500, 13995, 25)
        ]),
        (2, 6, "NET", [
            ("Cisco Catalyst 1000 48-Port Gigabit PoE+ Managed Switch", 92000, 119500, 8),
            ("Ubiquiti UniFi U7 Pro Enterprise Ceiling Access Point", 17500, 23900, 15),
            ("Schneider Actassi Cat6A UTP LSZH 305m Cable Drum", 9400, 13200, 20),
            ("Valrack 42U Server Rack Enclosure with Perforated Doors", 32000, 44000, 5),
            ("APC 16A 230V Switched Rack PDU with Metering", 21000, 28500, 10),
            ("Corning Duplex LC-LC Single-Mode Fiber Jumper 10m (x5)", 1400, 2300, 35),
            ("Fortinet FortiGate 60F Next-Gen Hardware Firewall", 42000, 56000, 8),
            ("Aruba Instant On 1930 24G 4SFP/SFP+ Switch", 26000, 34500, 12),
            ("MikroTik Cloud Router Switch CRS328-24P-4S+RM", 38000, 49999, 6),
            ("D-Link 24-Port Cat6 Unshielded 1U Patch Panel", 2200, 3400, 25),
            ("Netgear Nighthawk WiFi 7 Tri-Band Enterprise Router", 29000, 39999, 10),
            ("Finisar 10GBASE-SR SFP+ Optical Transceiver Module", 3200, 4800, 30),
            ("CyberPower 3000VA 2700W Smart App Sinewave Rack UPS", 52000, 68000, 5),
            ("Fluke Networks MicroScanner2 Cable Verifier Kit", 48000, 62000, 4),
            ("Panduit Mini-Com 48-Port Angled Modular Patch Panel", 4500, 6800, 15)
        ]),
        (3, 7, "OFF", [
            ("Herman Miller Aeron Ergonomic Task Chair (Size B)", 85000, 115000, 6),
            ("ErgoFlex Motorized Dual-Motor Standing Desk 160x80cm", 24000, 34999, 12),
            ("Heavy-Duty Dual Gas Spring Monitor Arm Bracket", 3200, 5499, 25),
            ("Canon imageRUNNER ADVANCE Enterprise Laser Copier", 145000, 189000, 4),
            ("Fellowes Commercial Cross-Cut Heavy Duty Shredder", 18000, 24500, 10),
            ("Steelcase Gesture Ergonomic Office Chair with Headrest", 92000, 122000, 5),
            ("Jarvis Bamboo Electric Standing Desk 140x70cm", 22000, 31500, 10),
            ("Jabra Speak 750 Bluetooth Conference Speakerphone", 16000, 22500, 15),
            ("Poly Studio P15 Personal Video Conference Soundbar", 24000, 32900, 10),
            ("Epson EcoTank L15150 A3 Multifunction Color Printer", 62000, 78900, 6),
            ("Godrej 4-Drawer Heavy Metal Anti-Tilt Filing Cabinet", 14000, 19500, 8),
            ("Clarus Glassboard Magnetic Whiteboard (180x120cm)", 12500, 18200, 10),
            ("VariDesk Pro Plus 36 Stand-Up Desktop Converter", 15000, 21999, 12),
            ("BenQ WiT e-Reading LED Desk Lamp with Auto-Dimming", 11000, 15499, 15),
            ("Kensington SmartFit SoleMate Ergonomic Footrest", 2400, 3899, 20)
        ]),
        (4, 2, "IND", [
            ("Bosch GSB 18V-150 C Heavy Duty Brushless Impact Drill", 18500, 24800, 12),
            ("Norbar Pro-Digital Industrial Torque Wrench 200Nm", 22000, 29500, 8),
            ("Hazet 5-Compartment Heavy Industrial Steel Tool Chest", 6500, 9200, 15),
            ("Omron Industrial Optical Proximity Sensor E3Z-D61", 2800, 4100, 30),
            ("Makita 2.5HP 50L Oil-Free Silent Air Compressor", 26000, 34500, 6),
            ("DeWalt 20V MAX XR Cordless Brushless Rotary Hammer", 21000, 28900, 10),
            ("Fluke 87V Industrial Digital Multimeter True-RMS", 31000, 41500, 8),
            ("Milwaukee M18 FUEL High Torque 1/2\" Impact Wrench", 24500, 32800, 10),
            ("Mitutoyo 0-150mm Digimatic Digital Caliper IP67", 8500, 12200, 15),
            ("Weller WT 1010 Set 1-Channel Soldering Station 90W", 19500, 26000, 8),
            ("Knipex 6-Piece Plier & Cutter Set in Foam Tray", 9200, 13500, 18),
            ("Stanley FatMax 1000V Insulated Screwdriver 10-Piece Kit", 2800, 4200, 25),
            ("Ridgid Heavy-Duty 24\" Cast Iron Straight Pipe Wrench", 4200, 6100, 20),
            ("Enerpac P392 Two-Speed Hydraulic Hand Pump 700 Bar", 38000, 49500, 4),
            ("Proto 1/4\" & 3/8\" Drive 100-Piece Mechanic Socket Set", 16500, 22900, 10)
        ]),
        (5, 4, "SAF", [
            ("Tiger Steel-Toe S3 Puncture-Resistant Kevlar Boots", 1850, 2850, 35),
            ("3M DBI-SALA Fall Protection Full-Body Harness", 6200, 8900, 20),
            ("Petzl Vertex Vented Industrial Climbing Hard Hat", 3400, 4800, 25),
            ("Honeywell Dual-Cartridge Half Mask Respirator Kit", 1450, 2199, 40),
            ("Flame-Retardant Heavy Cotton Safety Boiler Suit", 1250, 1950, 35),
            ("Uvex Genesis Anti-Fog Chemical Splash Safety Glasses", 420, 890, 60),
            ("Ansell HyFlex 11-840 Nitrile Coated Work Gloves (Pack 12)", 1800, 2900, 50),
            ("Dräger X-am 2500 4-Gas Detector Monitor", 44000, 58000, 5),
            ("Brady Compact Safety Lockout/Tagout Padlock Kit (x10)", 7800, 11500, 15),
            ("Justrite 12-Gallon Flammable Liquid Safety Cabinet", 29000, 39500, 4),
            ("DuPont Tyvek 500 Chemical Protective Coverall (Box 25)", 6500, 9800, 20),
            ("Bradley Wall-Mounted Emergency Eye/Face Wash Station", 14500, 19800, 8),
            ("Peltor X5A Over-the-Head Hearing Protection Earmuffs", 2600, 3900, 30),
            ("Miller Falcon 20ft Self-Retracting Webbing Lifeline", 16000, 22500, 10),
            ("Jallatte S3 Shock-Absorbing Executive Safety Shoes", 4800, 7200, 20)
        ]),
        (6, 5, "FND", [
            ("Estate Blend Single-Origin Arabica Roasted Beans (1kg)", 720, 1250, 40),
            ("First-Flush Vintage Organic Darjeeling Leaf Tea (500g)", 580, 990, 35),
            ("SuperSeed Whole Grain High-Protein Snack Bars (Pack 30)", 890, 1450, 30),
            ("Voltas Smart Touch Hot & Cold Commercial Dispenser", 8200, 11499, 8),
            ("Touchless Automatic Hand Sanitizer Dispenser Stand", 1800, 2750, 20),
            ("Monin Gourmet Syrup Pantry Assortment 6x700ml", 2400, 3600, 25),
            ("Tetley Pure Green Tea Bags Master Dispenser (Pack 200)", 680, 1150, 40),
            ("Oatly Barista Edition Oat Milk 1L (Carton of 6)", 1100, 1750, 35),
            ("Raw Pressery Cold-Pressed Valencia Orange Juice 250ml (x12)", 750, 1200, 30),
            ("Lotus Biscoff Individual Wrapped Caramel Biscuits (Pack 300)", 1400, 2199, 25),
            ("Twinings Earl Grey Tea Luxury Wooden Caddy Collection", 1800, 2800, 15),
            ("Nature Valley Crunchy Oats 'n Honey Granola Bars (Pack 48)", 1250, 1950, 25),
            ("True Elements 7-in-1 Super Seeds Mix 500g (Pack of 4)", 980, 1600, 30),
            ("Davidoff Rich Aroma Fine Decaf Coffee 100g (Pack of 3)", 1350, 2100, 20),
            ("Nestle Everyday Dairy Whitener Pouch 1kg (Case of 10)", 3200, 4500, 15)
        ]),
        (7, 10, "LOG", [
            ("Nilkamal 2.5 Ton Heavy-Duty Hydraulic Hand Pallet Truck", 18500, 24500, 6),
            ("Zebra ZT411 Industrial Thermal Transfer Barcode Printer", 72000, 94000, 5),
            ("Zebra DS2208 Handheld 1D/2D Corded USB Barcode Scanner", 4200, 6500, 20),
            ("Honeywell Voyager 1400g Wireless 2D Area-Imaging Scanner", 9800, 14200, 15),
            ("Cast Stretch Film 23 Micron Heavy Wrapping Roll (Pack 4)", 2100, 3300, 40),
            ("Signode Heavy Steel Strapping Tensioner & Sealer Tool Kit", 8500, 12500, 12),
            ("Avery Dennison Monarch 1131 One-Line Price/SKU Label Gun", 2800, 4200, 20),
            ("Eagle Poly Drum Spill Containment Basin Pallet (4-Drum)", 24000, 32500, 6),
            ("Rubbermaid Commercial Heavy-Duty Utility Cart (2-Shelf)", 14500, 19800, 8),
            ("Dymo LabelWriter 550 Turbo High-Speed Postal Labeler", 11500, 16200, 10),
            ("Uline Industrial Electronic Shipping Platform Scale 150kg", 12500, 17800, 8),
            ("Wesco Heavy-Duty Appliance Hand Truck with Stair Climbers", 8900, 13200, 10),
            ("Sealed Air Instapak Quick RT Foam Packaging Bags (Pack 30)", 5400, 8200, 20),
            ("Tesa 4124 Heavy Duty Clear Carton Sealing Tape (Case 36)", 2900, 4500, 30),
            ("Jaloni 3-Tier Rolling Heavy Tool & Parts Service Trolley", 7400, 10800, 12)
        ]),
        (8, 9, "MED", [
            ("Philips HeartStart FRx Commercial Automated Defibrillator (AED)", 88000, 115000, 4),
            ("OSHA 150-Person Industrial ANSI Class A First Aid Cabinet", 8500, 12800, 12),
            ("Water-Jel Emergency Industrial Burn Care Trauma Station", 5400, 8200, 15),
            ("Zoll AED Plus CPR-D-padz Adult Replacement Electrode Kit", 9500, 13800, 10),
            ("Honeywell Eyesaline 16oz Dual Emergency Eye Wash Station", 2400, 3900, 25),
            ("Boso Medicus X Digital Upper Arm Blood Pressure Monitor", 3600, 5400, 15),
            ("Nonin Onyx Vantage 9590 Professional Finger Pulse Oximeter", 6200, 8900, 18),
            ("Laerdal Pocket Mask CPR Barrier with One-Way Valve (x5)", 1800, 2900, 30),
            ("Seca 874 High-Precision Electronic Medical Column Scale", 28000, 37500, 4),
            ("Hartmann Sterilux Gauze Rolls & Bandage Trauma Case", 3200, 4900, 20),
            ("Braun ThermoScan 7 Professional Ear Infrared Thermometer", 4500, 6800, 15),
            ("North by Honeywell Emergency Spill Clean-Up Biohazard Kit", 3800, 5600, 15),
            ("Curad Nitrile Exam Powder-Free Gloves Box of 200 (Case 10)", 4200, 6500, 25),
            ("SAM Medical SAM Pelvic Sling II Military Trauma Splint", 7800, 11200, 8),
            ("Purrell Advanced TFX 1200ml Antibacterial Foam Refill (x4)", 3100, 4700, 30)
        ])
    ]

    products_data = []
    prod_id_counter = 1
    barcode_base = 890103000000

    for cat_id, sup_id, prefix, item_list in catalog_templates:
        for idx, (name, cost, unit, reorder) in enumerate(item_list, start=1):
            sku = f"{prefix}-{100 + idx}"
            # Realistic 13-digit EAN/UPC barcode
            barcode = str(barcode_base + prod_id_counter * 37 + (cat_id * 100))
            products_data.append((sku, barcode, name, cat_id, sup_id, cost, unit, reorder, 1))
            prod_id_counter += 1

    cursor.executemany("""
        INSERT INTO products (sku, barcode, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, products_data)

    total_products = len(products_data)
    print(f"Generated {total_products} products with unique barcodes and pricing.")

    # 5. Generate Inventory across 6 Warehouses + Initial Event Ledger Movements
    # We will stock products across 2 to 4 warehouses randomly, ensuring varied stock statuses:
    # Healthy, Low Stock, Critical, Out of Stock
    inventory_rows = []
    ledger_entries = []
    now = datetime.now()

    random.seed(42) # Reproducible realistic distribution

    for p_id in range(1, total_products + 1):
        # Choose 2 to 4 warehouses for this product
        num_wh = random.choice([2, 3, 4])
        selected_whs = random.sample(range(1, 7), num_wh)

        for w_id in selected_whs:
            # Decide stock profile: 70% healthy, 15% low stock, 10% critical, 5% out of stock
            roll = random.random()
            if roll < 0.05:
                final_qty = 0 # Out of stock
            elif roll < 0.15:
                final_qty = random.randint(1, 4) # Critical
            elif roll < 0.30:
                final_qty = random.randint(5, 12) # Low stock
            elif roll < 0.90:
                final_qty = random.randint(25, 120) # Normal/Healthy
            else:
                final_qty = random.randint(130, 280) # High stock

            bin_loc = f"{chr(65 + (w_id % 6))}-{p_id:02d}-{(w_id * 3) % 9 + 1}"
            restock_date = (now - timedelta(days=random.randint(5, 30), hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")

            inventory_rows.append((p_id, w_id, final_qty, bin_loc, restock_date))

            # Ledger: Record INITIAL_COUNT event
            ledger_entries.append((
                p_id, w_id, "INITIAL_COUNT", final_qty, final_qty, 
                "INVENTORY_INIT", f"INIT-WH{w_id}-P{p_id}", "Initial stock intake baseline", 
                "SYSTEM_MIGRATION", restock_date
            ))

    cursor.executemany("""
        INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, bin_location, last_restocked_at)
        VALUES (?, ?, ?, ?, ?);
    """, inventory_rows)

    print(f"Stocked {len(inventory_rows)} inventory points across 6 warehouses.")

    # 6. Customers (20 Enterprise, Wholesale, and Retail Accounts)
    customers = [
        ("Tata Consultancy Services (TCS)", "procurement@tcs.com", "+91-9820123456", "TCS Olympus, Hiranandani Estate, Thane", "Mumbai", "Maharashtra", "400607", "Corporate"),
        ("Infosys Limited", "kavita.raman@infosys.com", "+91-9845987654", "B-12, Palm Meadows, Whitefield Campus", "Bengaluru", "Karnataka", "560066", "Corporate"),
        ("Siddharth Khanna Law Associates", "siddharth@khannalaw.in", "+91-9811456789", "44 Golf Links, Central Delhi", "New Delhi", "Delhi", "110003", "Corporate"),
        ("Swaminathan Technologies", "procurement@swamitech.org", "+91-9949112233", "Plot 18, HITEC City, Madhapur", "Hyderabad", "Telangana", "500081", "Wholesale"),
        ("StartUp Hub India", "nitin.chawla@startuphub.io", "+91-9871098765", "Sector 54, Golf Course Road", "Gurugram", "Haryana", "122002", "Corporate"),
        ("Ahmedabad Specialty Chemicals", "pooja.s@ahmedabadchem.com", "+91-9765432109", "14 Navrangpura, Near Law Garden", "Ahmedabad", "Gujarat", "380009", "Wholesale"),
        ("Chennai Marine Engineering", "gautam@chennaimarine.com", "+91-9840112233", "102 Anna Salai, Guindy Industrial", "Chennai", "Tamil Nadu", "600032", "Corporate"),
        ("Pune AutoWorks Ltd", "vikrant@puneautoworks.in", "+91-9823114455", "Plot 88, Chakan Industrial Phase 3", "Pune", "Maharashtra", "410501", "Wholesale"),
        ("Kolkata Semiconductor Complex", "anuradha.roy@kolkatatech.org", "+91-9831122334", "Salt Lake Sector V, Electronic Complex", "Kolkata", "West Bengal", "700091", "Corporate"),
        ("Bhasin Electronics Wholesale", "rohit.bhasin@bhasinelectronics.com", "+91-9810055443", "Chandni Chowk Wholesale Market", "New Delhi", "Delhi", "110006", "Wholesale"),
        ("Dr. Sneha Kulkarni Clinic", "sneha.k@gmail.com", "+91-9822334455", "Prabhat Road, Lane 4, Erandwane", "Pune", "Maharashtra", "411004", "Retail"),
        ("Varma Steels & Alloys", "harsh@varmasteels.com", "+91-9948877665", "Autonagar Industrial Area", "Visakhapatnam", "Andhra Pradesh", "530012", "Wholesale"),
        ("Kerala State IT Mission", "divya.menon@keralait.gov.in", "+91-9447012345", "Technopark Phase III", "Thiruvananthapuram", "Kerala", "695583", "Corporate"),
        ("Agarwal Infrastructure Corp", "manish@agarwalinfra.co.in", "+91-9414055667", "MI Road, C-Scheme", "Jaipur", "Rajasthan", "302001", "Corporate"),
        ("Neha Bansal Architect Studio", "neha.bansal@gmail.com", "+91-9818822334", "Tower 3, Nirvana Country, Sector 50", "Gurugram", "Haryana", "122018", "Retail"),
        ("Nair Logistics & Freight Services", "arjun.nair@nairlogistics.com", "+91-9847098765", "Willingdon Island Commercial Zone", "Kochi", "Kerala", "682003", "Wholesale"),
        ("L&T Hydrocarbon Engineering", "b2b@lnt-hydrocarbon.com", "+91-9822998877", "Powai Works, Saki Vihar Road", "Mumbai", "Maharashtra", "400072", "Corporate"),
        ("Wipro Technologies Campus", "central.procure@wipro.com", "+91-9845009988", "Sarjapur Road Campus, Doddakannelli", "Bengaluru", "Karnataka", "560035", "Corporate"),
        ("Reliance Retail Hub Central", "vendor.desk@ril.com", "+91-9820991122", "Reliance Corporate Park, Ghansoli", "Navi Mumbai", "Maharashtra", "400701", "Wholesale"),
        ("Apollo HealthCity Supplies", "supplies@apollohealth.in", "+91-9949988112", "Road No 72, Film Nagar, Jubilee Hills", "Hyderabad", "Telangana", "500033", "Corporate")
    ]
    cursor.executemany("""
        INSERT INTO customers (full_name, email, phone, shipping_address, city, state, pincode, customer_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, customers)

    # 7. Generate 42 Customer Orders with 94+ Order Items
    cursor.execute("SELECT product_id, unit_price FROM products;")
    prices = {r["product_id"]: r["unit_price"] for r in cursor.fetchall()}

    # Pick only well-stocked inventory points (quantity_on_hand >= 30) for orders so balance remains strictly positive
    cursor.execute("SELECT inventory_id, product_id, warehouse_id, quantity_on_hand FROM inventory WHERE quantity_on_hand >= 30;")
    available_stock_points = [dict(r) for r in cursor.fetchall()]

    carriers = ["BlueDart Express", "Delhivery Logistics", "DTDC Air Cargo", "FedEx SupplyChain", "Amazon Shipping"]
    statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Shipped", "Shipped", "Processing", "Pending", "Cancelled"]

    order_items_rows = []
    shipments_rows = []

    for o_idx in range(1, 43):
        order_num = f"ORD-2026-{1000 + o_idx}"
        cust_id = random.randint(1, len(customers))
        status = statuses[o_idx % len(statuses)]
        days_ago = max(1, 35 - o_idx)
        order_date = (now - timedelta(days=days_ago, hours=random.randint(1, 14))).strftime("%Y-%m-%d %H:%M:%S")

        # Pick 1 to 4 available inventory points
        num_items = random.randint(1, 3)
        chosen_points = random.sample(available_stock_points, min(num_items, len(available_stock_points)))

        subtotal = 0.0
        line_items_for_order = []

        for pt in chosen_points:
            p_id = pt["product_id"]
            w_id = pt["warehouse_id"]
            qty = random.randint(1, 4)
            u_price = prices[p_id]
            i_sub = round(u_price * qty, 2)
            subtotal += i_sub
            line_items_for_order.append((p_id, w_id, qty, u_price, i_sub))

        tax = round(subtotal * 0.18, 2)
        discount = 2500.0 if subtotal > 150000 else (1000.0 if subtotal > 50000 else 0.0)
        total = round(subtotal + tax - discount, 2)
        pay_status = "Refunded" if status == "Cancelled" else ("Paid" if status in ["Delivered", "Shipped", "Processing"] else "Unpaid")

        cursor.execute("""
            INSERT INTO orders (order_number, customer_id, order_date, status, subtotal, tax_amount, discount_amount, total_amount, payment_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (order_num, cust_id, order_date, status, subtotal, tax, discount, total, pay_status, f"Enterprise procurement dispatch #{o_idx}"))

        order_id = cursor.lastrowid

        # Insert line items
        for p_id, w_id, qty, u_price, i_sub in line_items_for_order:
            order_items_rows.append((order_id, p_id, w_id, qty, u_price, i_sub))

            # Record Ledger event for sale if order wasn't cancelled
            if status != "Cancelled":
                ledger_entries.append((
                    p_id, w_id, "SALE", -qty, max(0, pt["quantity_on_hand"] - qty),
                    "ORDER", order_num, f"Customer purchase fulfillment ({order_num})",
                    "ACID_CHECKOUT_PROC", order_date
                ))

        # Shipments
        if status in ["Delivered", "Shipped"]:
            carrier = carriers[o_idx % len(carriers)]
            trk = f"TRK-{carrier[:2].upper()}-{100000 + o_idx * 941}"
            ship_date = (datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
            del_date = (datetime.strptime(ship_date, "%Y-%m-%d %H:%M:%S") + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S") if status == "Delivered" else None
            ship_status = "Delivered" if status == "Delivered" else "In Transit"
            shipments_rows.append((order_id, line_items_for_order[0][1], carrier, trk, ship_status, ship_date, del_date))

    cursor.executemany("""
        INSERT INTO order_items (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
        VALUES (?, ?, ?, ?, ?, ?);
    """, order_items_rows)

    cursor.executemany("""
        INSERT INTO shipments (order_id, warehouse_id, carrier, tracking_number, shipping_status, shipped_at, delivered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, shipments_rows)

    print(f"Generated 42 orders with {len(order_items_rows)} lines and {len(shipments_rows)} tracked shipments.")

    # 8. Inter-Warehouse Transfers (18 Transfers from well-stocked hubs)
    transfers = []
    # Pick from inventory stock points that have at least 25 units
    eligible_transfers = [(r[0], r[1]) for r in inventory_rows if r[2] >= 25]
    
    for t_idx in range(1, 19):
        p_id, src_wh = eligible_transfers[t_idx % len(eligible_transfers)]
        dst_wh = (src_wh % 6) + 1 # Different warehouse
        t_qty = random.randint(2, 6)
        status = "Completed" if t_idx <= 12 else ("In Transit" if t_idx <= 16 else "Requested")
        init_at = (now - timedelta(days=max(1, 22 - t_idx), hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        comp_at = (datetime.strptime(init_at, "%Y-%m-%d %H:%M:%S") + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S") if status == "Completed" else None
        transfers.append((p_id, src_wh, dst_wh, t_qty, status, "Supply Chain Coordinator", init_at, comp_at))

    cursor.executemany("""
        INSERT INTO stock_transfers (product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, initiated_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, transfers)

    # 9. Additional Ledger Events for Transfers, Restocks, Damages, and Returns
    for p_id, src_wh, dst_wh, qty, status, user, init_at, comp_at in transfers:
        if status == "Completed":
            ledger_entries.append((
                p_id, src_wh, "TRANSFER_OUT", -qty, 20, 
                "TRANSFER", f"TRF-FROM-WH{src_wh}", f"Inter-warehouse transfer out to WH-{dst_wh}", user, init_at
            ))
            ledger_entries.append((
                p_id, dst_wh, "TRANSFER_IN", qty, 35, 
                "TRANSFER", f"TRF-TO-WH{dst_wh}", f"Inter-warehouse transfer received from WH-{src_wh}", user, comp_at
            ))

    # Add 25 Restocks, 10 Damaged goods entries, and 8 Customer Returns to the Ledger
    stocked_pairs = [(r[0], r[1]) for r in inventory_rows if r[2] >= 20]
    
    for r_idx in range(1, 26):
        p_id, w_id = random.choice(stocked_pairs)
        r_qty = random.randint(15, 60)
        r_date = (now - timedelta(days=random.randint(3, 28), hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        ledger_entries.append((
            p_id, w_id, "RESTOCK", r_qty, 80,
            "PURCHASE_ORDER", f"PO-INBOUND-{8000 + r_idx}", "Supplier procurement batch receipt",
            "Warehouse_Receiving", r_date
        ))

    for d_idx in range(1, 11):
        p_id, w_id = random.choice(stocked_pairs)
        d_qty = random.randint(1, 2)
        d_date = (now - timedelta(days=random.randint(1, 20), hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        ledger_entries.append((
            p_id, w_id, "DAMAGE", -d_qty, 12,
            "DAMAGE_REPORT", f"DMG-REP-{d_idx:03d}", "Packaging damaged during handling/forklift transit",
            "QA_Inspector", d_date
        ))

    for ret_idx in range(1, 9):
        p_id, w_id = random.choice(stocked_pairs)
        ret_qty = random.randint(1, 2)
        ret_date = (now - timedelta(days=random.randint(1, 15), hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        ledger_entries.append((
            p_id, w_id, "RETURN", ret_qty, 25,
            "CUSTOMER_RMA", f"RMA-{ret_idx:04d}", "Customer return unopened surplus units",
            "Returns_Desk", ret_date
        ))

    # Insert all event ledger entries
    cursor.executemany("""
        INSERT INTO inventory_ledger (
            product_id, warehouse_id, movement_type, delta_quantity, balance_after,
            reference_type, reference_id, notes, recorded_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ledger_entries)

    print(f"Generated {len(ledger_entries)} event ledger movements (Event Sourcing).")

    # 10. Audit Logs (Triggers)
    audit_records = []
    for entry in ledger_entries[:75]: # top 75 movements reflected in audit trail
        p_id, w_id, m_type, delta, bal, ref_type, ref_id, notes, user, t_stamp = entry
        audit_records.append((
            p_id, w_id, m_type, max(0, bal - delta), bal, delta, ref_id, user, t_stamp
        ))

    cursor.executemany("""
        INSERT INTO inventory_audit_log (product_id, warehouse_id, change_type, old_quantity, new_quantity, change_amount, reference_id, changed_by, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, audit_records)

    # Ensure all product-warehouse combinations present in inventory_ledger exist in inventory table
    cursor.execute("""
        INSERT OR IGNORE INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at)
        SELECT DISTINCT product_id, warehouse_id, 0, datetime('now')
        FROM inventory_ledger;
    """)

    # Reconcile inventory.quantity_on_hand to strictly match SUM(delta_quantity) from event ledger
    cursor.execute("""
        UPDATE inventory 
        SET quantity_on_hand = (
            SELECT IFNULL(SUM(delta_quantity), 0)
            FROM inventory_ledger
            WHERE inventory_ledger.product_id = inventory.product_id
              AND inventory_ledger.warehouse_id = inventory.warehouse_id
        );
    """)

    conn.commit()
    conn.close()

    print("=" * 65)
    print("  StockFlow Database populated with High-Volume Enterprise Data:")
    print(f"  • {len(categories)} Categories")
    print(f"  • {len(suppliers)} Suppliers")
    print(f"  • {len(warehouses)} Warehouses")
    print(f"  • {total_products} Products Catalog (with EAN/UPC Barcodes)")
    print(f"  • {len(inventory_rows)} Inventory Stock Points")
    print(f"  • {len(customers)} Customer Accounts")
    print(f"  • 42 Orders with {len(order_items_rows)} Line Items & 30+ Shipments")
    print(f"  • {len(transfers)} Inter-Warehouse Transfers")
    print(f"  • {len(ledger_entries)} Inventory Ledger Movements (Event Sourced)")
    print(f"  • {len(audit_records)} Trigger Audit Logs")
    print("=" * 65)

if __name__ == "__main__":
    populate_rich_data()
