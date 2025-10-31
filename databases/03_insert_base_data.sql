-- ===================================================================================
-- 03_INSERT_BASE_DATA.SQL
-- Populates the database with the minimum data required to run the application.
-- ===================================================================================

USE plm;

-- Disable checks for bulk inserts
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- ===================================================================================
-- 1. CORE ENTITIES
-- ===================================================================================

-- Parking_Lot (ID 1)
INSERT INTO Parking_Lot (Lot_ID, Name, Total_spaces, Address) VALUES
(1, 'Central Business Lot', 500, '450 University Ave, City Center');

-- Employee (Setup Hierarchy with final roles)
INSERT INTO Employee (EmployeeID, Name, Role, ManagerID) VALUES
(1, 'Alice Johnson', 'Admin', NULL),      -- Top level, Admin
(2, 'Bob Williams', 'Manager', 1),     -- Reports to Alice
(3, 'Charlie Davis', 'Supervisor', 2),
(4, 'Nithin K S','Admin',NULL); -- Reports to Bob


-- Users (Security Demo Setup)
-- Passwords are 'password123', 'securepass', 'charliepass'. 
-- The hash_password_on_insert trigger will handle them.
INSERT INTO Users (username, hashed_password, EmployeeID) VALUES
('alice.j', 'password123', 1),
('bob.w', 'securepass', 2),
('charlie.d', 'charliepass', 3),
('nithin_7','Nithin@2005',4);



-- Customer (Includes the vital Walk-In Customer ID 9999)
INSERT INTO Customer (CustomerID, Name, Phone, Email, Street, City, State, ZIP) VALUES
(1001, 'Dr. Emily Carter', '555-1234', 'e.carter@email.com', '10 Technology Blvd', 'Tech City', 'CA', '90210'),
(1002, 'John Smith', '555-5678', 'john.s@mail.net', '20 Main St', 'Downtown', 'NY', '10001'),
(9999, 'Walk-In Customer', NULL, NULL, NULL, NULL, NULL, NULL);

-- Service (Includes Cost)
INSERT INTO Service (Name, Description, Cost) VALUES
('EV Charging', 'Level 2 electric vehicle charging.', 20.00),
('Car Wash', 'Basic exterior car wash service.', 15.00);

-- ===================================================================================
-- 2. DEPENDENT ENTITIES
-- ===================================================================================

-- Parking_Space (All spaces, including the 15+ we added)
INSERT INTO Parking_Space (SpaceID, Lot_ID, SpaceNumber, SpaceType, Status) VALUES
(301, 1, 301, 'Standard', 'Vacant'),
(302, 1, 302, 'Standard', 'Vacant'),
(303, 1, 303, 'Standard', 'Vacant'),
(401, 1, 401, 'Handicap', 'Vacant'),
(402, 1, 402, 'EV', 'Vacant'),
(403, 1, 403, 'Standard', 'Vacant'),
(404, 1, 404, 'Standard', 'Vacant'),
(405, 1, 405, 'Standard', 'Vacant'),
(406, 1, 406, 'Standard', 'Vacant'),
(407, 1, 407, 'Standard', 'Vacant'),
(408, 1, 408, 'Standard', 'Vacant'),
(409, 1, 409, 'Standard', 'Vacant'),
(410, 1, 410, 'Standard', 'Vacant'),
(411, 1, 411, 'Standard', 'Vacant'),
(412, 1, 412, 'Standard', 'Vacant'),
(413, 1, 413, 'Standard', 'Vacant'),
(414, 1, 414, 'Standard', 'Vacant'),
(415, 1, 415, 'Standard', 'Vacant');

-- Vehicle (Owned by Customers)
INSERT INTO Vehicle (LicensePlate, CustomerID, Make, Model, Color) VALUES
('LICENSE-101', 1001, 'Toyota', 'Camry', 'Silver'),
('LICENSE-102', 1002, 'Ford', 'F-150', 'Black'),
('ABC-789', 9999, 'Walk-In', 'Unspecified', 'N/A');

-- ===================================================================================
-- 3. TRANSACTIONAL & RELATIONSHIP DATA (For Testing)
-- ===================================================================================

-- Setup a pre-existing Parking_Record (for testing exit)
INSERT INTO Parking_Record (LicensePlate, SpaceID, EntryTime, ExitTime, Duration, PaymentID)
VALUES ('LICENSE-101', 401, NOW() - INTERVAL 90 MINUTE, NULL, NULL, NULL);

-- Manually update the space status (the trigger only fires on INSERT)
UPDATE Parking_Space
SET Status = 'Occupied'
WHERE SpaceID = 401;

-- Maintenance_Log (For testing reports)
INSERT INTO Maintenance_Log (SpaceID, LogID, Cost, Description, Maintenance_data) VALUES
(402, 1, 50.00, 'Minor EV charger repair', CURDATE());

-- Customer_Service (For testing M:N relationship)
INSERT INTO Customer_Service (CustomerID, ServiceID) VALUES
(1001, 1), -- Emily uses EV Charging
(1002, 2); -- John uses Car Wash

-- Final clean up
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

SELECT 'Base data inserted successfully.' AS Status;
