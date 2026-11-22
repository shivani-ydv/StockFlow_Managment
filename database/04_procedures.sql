-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 04_procedures.sql
-- Description: Stored procedures with ACID transaction blocks, error handling,
--              concurrency row locks (FOR UPDATE), and business validation.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

USE stockflow_db;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- Procedure 1: sp_place_single_item_order
-- Purpose: Places a customer order atomically. Demonstrates ACID compliance.
-- Parameters:
--   p_customer_id, p_product_id, p_warehouse_id, p_quantity, p_notes,
--   OUT o_order_id, OUT o_status_code, OUT o_status_message
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_place_single_item_order$$
CREATE PROCEDURE sp_place_single_item_order(
    IN p_customer_id INT,
    IN p_product_id INT,
    IN p_warehouse_id INT,
    IN p_quantity INT,
    IN p_notes TEXT,
    OUT o_order_id INT,
    OUT o_status_code VARCHAR(20),
    OUT o_status_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_current_stock INT DEFAULT 0;
    DECLARE v_unit_price DECIMAL(10, 2) DEFAULT 0.00;
    DECLARE v_subtotal DECIMAL(10, 2) DEFAULT 0.00;
    DECLARE v_order_num VARCHAR(50);
    DECLARE v_customer_exists INT DEFAULT 0;

    -- Exit handler for any unexpected SQL Exception (Rollback transaction)
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET o_order_id = NULL;
        SET o_status_code = 'SQL_ERROR';
        SET o_status_message = 'An unexpected database error occurred. Transaction rolled back.';
    END;

    -- Step 1: Input Validation
    IF p_quantity <= 0 THEN
        SET o_order_id = NULL;
        SET o_status_code = 'INVALID_QTY';
        SET o_status_message = 'Order quantity must be greater than zero.';
        LEAVE proc_label;
    END IF;

    SELECT COUNT(*) INTO v_customer_exists FROM customers WHERE customer_id = p_customer_id;
    IF v_customer_exists = 0 THEN
        SET o_order_id = NULL;
        SET o_status_code = 'CUSTOMER_NOT_FOUND';
        SET o_status_message = 'Specified customer ID does not exist.';
        LEAVE proc_label;
    END IF;

    -- Step 2: Start ACID Transaction
    START TRANSACTION;

    -- Step 3: Check and acquire row lock on product price and inventory
    SELECT unit_price INTO v_unit_price 
    FROM products 
    WHERE product_id = p_product_id AND is_active = TRUE;

    IF v_unit_price IS NULL THEN
        ROLLBACK;
        SET o_order_id = NULL;
        SET o_status_code = 'PRODUCT_NOT_FOUND';
        SET o_status_message = 'Product not found or currently inactive.';
        LEAVE proc_label;
    END IF;

    -- Row lock on inventory to prevent race conditions (lost update anomaly)
    SELECT quantity_on_hand INTO v_current_stock
    FROM inventory
    WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id
    FOR UPDATE;

    IF v_current_stock IS NULL OR v_current_stock < p_quantity THEN
        ROLLBACK;
        SET o_order_id = NULL;
        SET o_status_code = 'INSUFFICIENT_STOCK';
        SET o_status_message = CONCAT('Insufficient stock in warehouse. Available: ', IFNULL(v_current_stock, 0));
        LEAVE proc_label;
    END IF;

    -- Step 4: Decrement Inventory
    UPDATE inventory 
    SET quantity_on_hand = quantity_on_hand - p_quantity
    WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;

    -- Step 5: Generate Order Number and Header
    SET v_order_num = CONCAT('ORD-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), '-', FLOOR(RAND() * 899 + 100));
    SET v_subtotal = ROUND(v_unit_price * p_quantity, 2);

    INSERT INTO orders (order_number, customer_id, order_date, status, subtotal, tax_amount, total_amount, payment_status, notes)
    VALUES (v_order_num, p_customer_id, NOW(), 'Processing', v_subtotal, 0.00, v_subtotal, 'Paid', p_notes);

    SET o_order_id = LAST_INSERT_ID();

    -- Step 6: Insert Order Item (Trigger will calculate GST & update total_amount)
    INSERT INTO order_items (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
    VALUES (o_order_id, p_product_id, p_warehouse_id, p_quantity, v_unit_price, v_subtotal);

    -- Step 7: Commit Transaction
    COMMIT;

    SET o_status_code = 'SUCCESS';
    SET o_status_message = CONCAT('Order ', v_order_num, ' successfully created and stock updated.');
END$$

-- ----------------------------------------------------------------------------
-- Procedure 2: sp_transfer_inventory
-- Purpose: Safely moves stock between warehouses with atomicity and validation.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_transfer_inventory$$
CREATE PROCEDURE sp_transfer_inventory(
    IN p_product_id INT,
    IN p_from_wh_id INT,
    IN p_to_wh_id INT,
    IN p_quantity INT,
    IN p_user VARCHAR(80),
    OUT o_transfer_id INT,
    OUT o_status_code VARCHAR(20),
    OUT o_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_src_stock INT DEFAULT 0;
    DECLARE v_dst_exists INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET o_status_code = 'ERROR';
        SET o_message = 'Failed to execute stock transfer. Transaction rolled back.';
    END;

    IF p_from_wh_id = p_to_wh_id THEN
        SET o_status_code = 'INVALID_TRANSFER';
        SET o_message = 'Source and destination warehouses cannot be the same.';
        LEAVE proc_label;
    END IF;

    IF p_quantity <= 0 THEN
        SET o_status_code = 'INVALID_QUANTITY';
        SET o_message = 'Transfer quantity must be positive.';
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    -- Lock source inventory
    SELECT quantity_on_hand INTO v_src_stock
    FROM inventory
    WHERE product_id = p_product_id AND warehouse_id = p_from_wh_id
    FOR UPDATE;

    IF v_src_stock IS NULL OR v_src_stock < p_quantity THEN
        ROLLBACK;
        SET o_status_code = 'INSUFFICIENT_STOCK';
        SET o_message = CONCAT('Source warehouse has insufficient stock. Available: ', IFNULL(v_src_stock, 0));
        LEAVE proc_label;
    END IF;

    -- Ensure destination inventory record exists or initialize
    SELECT COUNT(*) INTO v_dst_exists
    FROM inventory
    WHERE product_id = p_product_id AND warehouse_id = p_to_wh_id;

    IF v_dst_exists = 0 THEN
        INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand)
        VALUES (p_product_id, p_to_wh_id, 0);
    END IF;

    -- Deduct from Source
    UPDATE inventory 
    SET quantity_on_hand = quantity_on_hand - p_quantity
    WHERE product_id = p_product_id AND warehouse_id = p_from_wh_id;

    -- Add to Destination
    UPDATE inventory 
    SET quantity_on_hand = quantity_on_hand + p_quantity,
        last_restocked_at = NOW()
    WHERE product_id = p_product_id AND warehouse_id = p_to_wh_id;

    -- Record transfer log
    INSERT INTO stock_transfers (
        product_id, source_warehouse_id, destination_warehouse_id, quantity, status, initiated_by, completed_at
    ) VALUES (
        p_product_id, p_from_wh_id, p_to_wh_id, p_quantity, 'Completed', p_user, NOW()
    );

    SET o_transfer_id = LAST_INSERT_ID();

    COMMIT;
    SET o_status_code = 'SUCCESS';
    SET o_message = 'Stock successfully transferred and reconciled.';
END$$

-- ----------------------------------------------------------------------------
-- Procedure 3: sp_restock_product
-- Purpose: Restocks a product in a specified warehouse from a supplier shipment.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_restock_product$$
CREATE PROCEDURE sp_restock_product(
    IN p_product_id INT,
    IN p_warehouse_id INT,
    IN p_quantity INT,
    OUT o_new_quantity INT,
    OUT o_status_code VARCHAR(20)
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;

    IF p_quantity <= 0 THEN
        SET o_status_code = 'INVALID_QTY';
    ELSE
        SELECT COUNT(*) INTO v_exists
        FROM inventory
        WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;

        IF v_exists = 0 THEN
            INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, last_restocked_at)
            VALUES (p_product_id, p_warehouse_id, p_quantity, NOW());
        ELSE
            UPDATE inventory
            SET quantity_on_hand = quantity_on_hand + p_quantity,
                last_restocked_at = NOW()
            WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;
        END IF;

        SELECT quantity_on_hand INTO o_new_quantity
        FROM inventory
        WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;

        SET o_status_code = 'SUCCESS';
    END IF;
END$$

DELIMITER ;
