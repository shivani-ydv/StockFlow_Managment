-- ============================================================================
-- StockFlow - Smart Inventory & Order Management System
-- Script: 03_triggers.sql
-- Description: Automated business rules, constraints, and audit logging using
--              BEFORE / AFTER INSERT, UPDATE, and DELETE database triggers.
-- Target DBMS: MySQL 8.0+
-- ============================================================================

USE stockflow_db;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- Trigger 1: trg_audit_inventory_update
-- Purpose: Automatically logs whenever stock changes in the inventory table.
-- Type: AFTER UPDATE
-- Demonstrates: Auditing, OLD vs NEW keywords, system tracking.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_inventory_update$$
CREATE TRIGGER trg_audit_inventory_update
AFTER UPDATE ON inventory
FOR EACH ROW
BEGIN
    DECLARE v_change_type VARCHAR(30);
    DECLARE v_diff INT;

    SET v_diff = NEW.quantity_on_hand - OLD.quantity_on_hand;

    IF v_diff <> 0 THEN
        IF v_diff < 0 THEN
            SET v_change_type = 'ORDER_DEDUCT';
        ELSE
            SET v_change_type = 'RESTOCK';
        END IF;

        INSERT INTO inventory_audit_log (
            product_id,
            warehouse_id,
            change_type,
            old_quantity,
            new_quantity,
            change_amount,
            reference_id,
            changed_by,
            timestamp
        ) VALUES (
            NEW.product_id,
            NEW.warehouse_id,
            v_change_type,
            OLD.quantity_on_hand,
            NEW.quantity_on_hand,
            v_diff,
            CONCAT('INV-MOD-', NEW.inventory_id),
            USER(),
            NOW()
        );
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- Trigger 2: trg_prevent_negative_stock
-- Purpose: Prevents inventory from going negative at the database engine level.
-- Type: BEFORE UPDATE
-- Demonstrates: SIGNAL SQLSTATE exception throwing, data integrity protection.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_negative_stock$$
CREATE TRIGGER trg_prevent_negative_stock
BEFORE UPDATE ON inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity_on_hand < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Operation Aborted: Stock quantity cannot be negative.';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- Trigger 3: trg_update_order_totals
-- Purpose: Automatically updates order subtotal, tax (18%), and total_amount
--          when line items are inserted.
-- Type: AFTER INSERT ON order_items
-- Demonstrates: Computed financial rollups.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_update_order_totals$$
CREATE TRIGGER trg_update_order_totals
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE v_new_subtotal DECIMAL(12, 2);
    DECLARE v_tax DECIMAL(10, 2);

    -- Calculate total subtotal from all items in this order
    SELECT SUM(subtotal) INTO v_new_subtotal
    FROM order_items
    WHERE order_id = NEW.order_id;

    -- Standard 18% GST calculation (common in Indian academic projects)
    SET v_tax = ROUND(v_new_subtotal * 0.18, 2);

    UPDATE orders 
    SET 
        subtotal = v_new_subtotal,
        tax_amount = v_tax,
        total_amount = v_new_subtotal + v_tax - discount_amount
    WHERE order_id = NEW.order_id;
END$$

DELIMITER ;
