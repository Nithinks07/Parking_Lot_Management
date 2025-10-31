-- ===================================================================================
-- 02_CREATE_LOGIC.SQL
-- Creates all triggers, functions, and stored procedures used by the application.
-- ===================================================================================

USE plm;

-- Initialize session variable for security checks
SET @current_user_employee_id = NULL;

-- ===================================================================================
-- TRIGGERS
-- ===================================================================================

DELIMITER //
CREATE TRIGGER hash_password_on_insert
BEFORE INSERT ON Users
FOR EACH ROW
BEGIN
    IF NEW.hashed_password IS NOT NULL THEN
        SET NEW.hashed_password = SHA2(NEW.hashed_password, 256);
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_parking_space_status
AFTER INSERT ON Parking_Record
FOR EACH ROW
BEGIN
    UPDATE Parking_Space
    SET Status = 'Occupied'
    WHERE SpaceID = NEW.SpaceID;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER increment_payment_count
AFTER INSERT ON Payment
FOR EACH ROW
BEGIN
    DECLARE v_customer_id INT;

    SELECT v.CustomerID INTO v_customer_id
    FROM Parking_Record pr
    JOIN Vehicle v ON pr.LicensePlate = v.LicensePlate
    WHERE pr.RecordID = NEW.RecordID;

    UPDATE Customer
    SET PaymentCount = PaymentCount + 1
    WHERE CustomerID = v_customer_id;
END //
DELIMITER ;

-- ===================================================================================
-- PROCEDURES
-- ===================================================================================

DELIMITER //
CREATE PROCEDURE AuthenticateUser(
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE v_is_authenticated BOOLEAN DEFAULT FALSE;
    DECLARE v_stored_hash VARCHAR(255);
    DECLARE v_employee_id_found INT;
    
    SET @current_user_employee_id = NULL;

    SELECT u.hashed_password, u.EmployeeID
    INTO v_stored_hash, v_employee_id_found
    FROM Users u
    WHERE u.username = p_username;

    IF v_stored_hash IS NOT NULL AND v_stored_hash = SHA2(p_password, 256) THEN
        SET v_is_authenticated = TRUE;
        SET @current_user_employee_id = v_employee_id_found;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CreateUserAndEmployee(
    IN p_name VARCHAR(100),
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255)
)
main_block: BEGIN
    DECLARE v_employee_id INT;
    
    IF EXISTS (SELECT 1 FROM Users WHERE username = p_username) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists.';
        LEAVE main_block;
    END IF;

    START TRANSACTION;
    INSERT INTO Employee (Name, Role, ManagerID)
    VALUES (p_name, 'Attendant', 2); -- New users default to Attendant reporting to Manager (ID 2)
    
    SET v_employee_id = LAST_INSERT_ID();
    
    INSERT INTO Users (username, hashed_password, EmployeeID)
    VALUES (p_username, p_password, v_employee_id);
    
    COMMIT;
    
    SELECT 'Registration successful' AS Message, v_employee_id AS NewEmployeeID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddCustomer(
    IN p_customer_id INT, IN p_name VARCHAR(100), IN p_phone VARCHAR(20), IN p_email VARCHAR(100),
    IN p_street VARCHAR(100), IN p_city VARCHAR(100), IN p_state VARCHAR(50), IN p_zip VARCHAR(10)
)
main_block: BEGIN
    IF EXISTS (SELECT 1 FROM Customer WHERE CustomerID = p_customer_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer ID already exists.';
        LEAVE main_block;
    END IF;
    IF p_email IS NOT NULL AND p_email != '' AND EXISTS (SELECT 1 FROM Customer WHERE Email = p_email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already exists.';
        LEAVE main_block;
    END IF;
    INSERT INTO Customer (CustomerID, Name, Phone, Email, Street, City, State, ZIP, PaymentCount)
    VALUES (p_customer_id, p_name, p_phone, p_email, p_street, p_city, p_state, p_zip, 0);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddVehicle(
    IN p_license_plate VARCHAR(15), IN p_customer_id INT, IN p_make VARCHAR(50),
    IN p_model VARCHAR(50), IN p_color VARCHAR(50)
)
main_block: BEGIN
    IF NOT EXISTS (SELECT 1 FROM Customer WHERE CustomerID = p_customer_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer ID not found.';
        LEAVE main_block;
    END IF;
    IF EXISTS (SELECT 1 FROM Vehicle WHERE LicensePlate = p_license_plate) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'License Plate already exists.';
        LEAVE main_block;
    END IF;
    INSERT INTO Vehicle (LicensePlate, CustomerID, Make, Model, Color)
    VALUES (p_license_plate, p_customer_id, p_make, p_model, p_color);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AssignServiceToCustomer(
    IN p_customer_id INT, IN p_service_id INT
)
main_block: BEGIN
    IF NOT EXISTS (SELECT 1 FROM Customer WHERE CustomerID = p_customer_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer ID not found.';
        LEAVE main_block;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Service WHERE ServiceID = p_service_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Service ID not found.';
        LEAVE main_block;
    END IF;
    IF EXISTS (SELECT 1 FROM Customer_Service WHERE CustomerID = p_customer_id AND ServiceID = p_service_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer is already assigned to this service.';
        LEAVE main_block;
    END IF;
    INSERT INTO Customer_Service (CustomerID, ServiceID)
    VALUES (p_customer_id, p_service_id);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddService(
    IN p_name VARCHAR(100), IN p_description TEXT, IN p_cost DECIMAL(10, 2)
)
BEGIN
    INSERT INTO Service (Name, Description, Cost)
    VALUES (p_name, p_description, p_cost);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetServiceByID( IN p_service_id INT )
BEGIN
    SELECT * FROM Service WHERE ServiceID = p_service_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateService(
    IN p_service_id INT, IN p_name VARCHAR(100), IN p_description TEXT, IN p_cost DECIMAL(10, 2)
)
BEGIN
    UPDATE Service
    SET Name = p_name, Description = p_description, Cost = p_cost
    WHERE ServiceID = p_service_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteService( IN p_service_id INT )
BEGIN
    DELETE FROM Customer_Service WHERE ServiceID = p_service_id;
    DELETE FROM Service WHERE ServiceID = p_service_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CreateMaintenanceLog(
    IN p_space_id INT, IN p_description TEXT, IN p_cost DECIMAL(10, 2)
)
main_block: BEGIN
    DECLARE v_new_log_id INT DEFAULT 1;
    IF NOT EXISTS (SELECT 1 FROM Parking_Space WHERE SpaceID = p_space_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Parking Space ID not found.';
        LEAVE main_block;
    END IF;
    SELECT COALESCE(MAX(LogID), 0) + 1 INTO v_new_log_id
    FROM Maintenance_Log WHERE SpaceID = p_space_id;
    START TRANSACTION;
    INSERT INTO Maintenance_Log (SpaceID, LogID, Cost, Description, Maintenance_data)
    VALUES (p_space_id, v_new_log_id, p_cost, p_description, CURDATE());
    UPDATE Parking_Space SET Status = 'Maintenance' WHERE SpaceID = p_space_id;
    COMMIT;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE CompleteMaintenance( IN p_space_id INT )
main_block: BEGIN
    IF NOT EXISTS (SELECT 1 FROM Parking_Space WHERE SpaceID = p_space_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Parking Space ID not found.';
        LEAVE main_block;
    END IF;
    UPDATE Parking_Space SET Status = 'Vacant' WHERE SpaceID = p_space_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetCustomerByID( IN p_customer_id INT )
BEGIN
    SELECT * FROM Customer WHERE CustomerID = p_customer_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateCustomer(
    IN p_customer_id INT, IN p_name VARCHAR(100), IN p_phone VARCHAR(20), IN p_email VARCHAR(100),
    IN p_street VARCHAR(100), IN p_city VARCHAR(100), IN p_state VARCHAR(50), IN p_zip VARCHAR(10)
)
BEGIN
    UPDATE Customer
    SET Name = p_name, Phone = p_phone, Email = p_email, Street = p_street,
        City = p_city, State = p_state, ZIP = p_zip
    WHERE CustomerID = p_customer_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteCustomer( IN p_customer_id INT )
main_block: BEGIN
    IF EXISTS (SELECT 1 FROM Vehicle WHERE CustomerID = p_customer_id) THEN
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Cannot delete customer: They still own vehicles. Delete their vehicles first.';
        LEAVE main_block;
    END IF;
    START TRANSACTION;
    DELETE FROM Customer_Service WHERE CustomerID = p_customer_id;
    DELETE FROM Books WHERE CustomerID = p_customer_id;
    DELETE FROM Customer WHERE CustomerID = p_customer_id;
    COMMIT;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetVehicleByLicensePlate( IN p_license_plate VARCHAR(15) )
BEGIN
    SELECT * FROM Vehicle WHERE LicensePlate = p_license_plate;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateVehicle(
    IN p_original_license_plate VARCHAR(15), IN p_new_license_plate VARCHAR(15), IN p_customer_id INT,
    IN p_make VARCHAR(50), IN p_model VARCHAR(50), IN p_color VARCHAR(50)
)
BEGIN
    UPDATE Vehicle
    SET LicensePlate = p_new_license_plate, CustomerID = p_customer_id, Make = p_make,
        Model = p_model, Color = p_color
    WHERE LicensePlate = p_original_license_plate;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteVehicle( IN p_license_plate VARCHAR(15) )
main_block: BEGIN
    IF EXISTS (SELECT 1 FROM Parking_Record WHERE LicensePlate = p_license_plate) THEN
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Cannot delete vehicle: It has parking records.';
        LEAVE main_block;
    END IF;
    START TRANSACTION;
    DELETE FROM Books WHERE LicensePlate = p_license_plate;
    DELETE FROM Vehicle WHERE LicensePlate = p_license_plate;
    COMMIT;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAllParkingLots()
BEGIN
    SELECT Lot_ID, Name, Total_spaces, Address 
    FROM Parking_Lot ORDER BY Lot_ID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetParkingLotByID( IN p_lot_id INT )
BEGIN
    SELECT * FROM Parking_Lot WHERE Lot_ID = p_lot_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddParkingLot(
    IN p_lot_id INT, IN p_name VARCHAR(255), IN p_total_spaces INT, IN p_address VARCHAR(255)
)
BEGIN
    INSERT INTO Parking_Lot (Lot_ID, Name, Total_spaces, Address)
    VALUES (p_lot_id, p_name, p_total_spaces, p_address);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE UpdateParkingLot(
    IN p_lot_id INT, IN p_name VARCHAR(255), IN p_total_spaces INT, IN p_address VARCHAR(255)
)
BEGIN
    UPDATE Parking_Lot
    SET Name = p_name, Total_spaces = p_total_spaces, Address = p_address
    WHERE Lot_ID = p_lot_id;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE DeleteParkingLot( IN p_lot_id INT )
main_block: BEGIN
    IF EXISTS (SELECT 1 FROM Parking_Space WHERE Lot_ID = p_lot_id) THEN
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Cannot delete lot: It still contains parking spaces. Delete all spaces first.';
        LEAVE main_block;
    END IF;
    DELETE FROM Parking_Lot WHERE Lot_ID = p_lot_id;
END //
DELIMITER ;


SELECT 'Logic (Procedures, Triggers) created successfully.' AS Status;
