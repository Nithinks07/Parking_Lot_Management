-- ===================================================================================
-- 05_RESET_DATABASE.SQL
-- This script completely WIPES all transactional data for a clean test run.
-- Run this script, then run 03_insert_base_data.sql to repopulate.
-- ===================================================================================

USE plm;

-- Disable checks to allow TRUNCATE
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

SELECT '--- 1. Deleting all transactional data...' AS Status;

-- Delete data in order of dependency (child tables first)
TRUNCATE TABLE Payment;
TRUNCATE TABLE Parking_Record;
TRUNCATE TABLE Books;
TRUNCATE TABLE Customer_Service;
TRUNCATE TABLE Maintenance_Log;

SELECT '--- 2. Deleting all core data...' AS Status;

-- Now delete data from parent tables
TRUNCATE TABLE Users;
TRUNCATE TABLE Vehicle;
TRUNCATE TABLE Customer;
TRUNCATE TABLE Employee;
TRUNCATE TABLE Service;
TRUNCATE TABLE Parking_Space;
TRUNCATE TABLE Parking_Lot;

SELECT '--- 3. Resetting AUTO_INCREMENT values...' AS Status;

-- Reset AUTO_INCREMENT counters for a true fresh start
ALTER TABLE Employee AUTO_INCREMENT = 1;
ALTER TABLE Users AUTO_INCREMENT = 1;
ALTER TABLE Service AUTO_INCREMENT = 1;
ALTER TABLE Payment AUTO_INCREMENT = 1;
ALTER TABLE Parking_Record AUTO_INCREMENT = 1;

-- Re-enable checks
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

SELECT '*** DATABASE RESET COMPLETE ***' AS Status;
SELECT 'You can now safely run 03_insert_base_data.sql' AS Next_Step;
