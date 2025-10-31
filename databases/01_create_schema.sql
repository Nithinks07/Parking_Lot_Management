-- ===================================================================================
-- 01_CREATE_SCHEMA.SQL
-- Creates the database and all tables with their final, correct structure.
-- ===================================================================================

-- Create a fresh database
DROP DATABASE IF EXISTS plm;
CREATE DATABASE plm;
USE plm;

-- Disable checks for bulk table creation
SET FOREIGN_KEY_CHECKS = 0;

-- ===================================================================================
-- 1. CORE ENTITIES
-- ===================================================================================

CREATE TABLE Parking_Lot (
    Lot_ID INT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Total_spaces INT NOT NULL,
    Address VARCHAR(255)
);

CREATE TABLE Employee (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(100),
    ManagerID INT NULL -- Self-referencing FK added later
);

CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Phone VARCHAR(20),
    Email VARCHAR(100) UNIQUE,
    Street VARCHAR(100),
    City VARCHAR(100),
    State VARCHAR(50),
    ZIP VARCHAR(10),
    PaymentCount INT DEFAULT 0 NOT NULL -- Added from our updates
);

CREATE TABLE Service (
    ServiceID INT AUTO_INCREMENT PRIMARY KEY, -- Fixed to be AUTO_INCREMENT
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00 -- Added from our updates
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    EmployeeID INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================================
-- 2. DEPENDENT ENTITIES
-- ===================================================================================

CREATE TABLE Parking_Space (
    SpaceID INT PRIMARY KEY,
    Lot_ID INT NOT NULL,
    SpaceNumber INT NOT NULL,
    SpaceType ENUM('Standard', 'Handicap', 'EV', 'Reserved') NOT NULL,
    Status ENUM('Vacant', 'Occupied', 'Reserved', 'Maintenance') DEFAULT 'Vacant' NOT NULL,
    UNIQUE KEY (Lot_ID, SpaceNumber),
    FOREIGN KEY (Lot_ID) REFERENCES Parking_Lot(Lot_ID) ON DELETE RESTRICT
);

CREATE TABLE Vehicle (
    LicensePlate VARCHAR(15) PRIMARY KEY,
    CustomerID INT NOT NULL,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Color VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE RESTRICT
);

CREATE TABLE Maintenance_Log (
    SpaceID INT NOT NULL,
    LogID INT NOT NULL,
    Cost DECIMAL(10, 2) NOT NULL,
    Description TEXT,
    Maintenance_data DATE NOT NULL,
    PRIMARY KEY (SpaceID, LogID),
    FOREIGN KEY (SpaceID) REFERENCES Parking_Space(SpaceID) ON DELETE CASCADE
);

CREATE TABLE Customer_Service (
    CustomerID INT NOT NULL,
    ServiceID INT NOT NULL,
    PRIMARY KEY (CustomerID, ServiceID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (ServiceID) REFERENCES Service(ServiceID) ON DELETE CASCADE
);

CREATE TABLE Books (
    CustomerID INT NOT NULL,
    SpaceID INT NOT NULL,
    EmployeeID INT NOT NULL,
    LicensePlate VARCHAR(15) NULL, -- Added from our updates
    ReservationTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Notes TEXT,
    PRIMARY KEY (CustomerID, SpaceID, EmployeeID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (SpaceID) REFERENCES Parking_Space(SpaceID) ON DELETE RESTRICT,
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE RESTRICT
);

-- ===================================================================================
-- 3. TRANSACTIONAL ENTITIES (Inter-dependent)
-- ===================================================================================

CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    RecordID INT UNIQUE NOT NULL, -- FK added later
    Amount DECIMAL(10, 2) NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    Method ENUM('Credit Card', 'Cash', 'UPI', 'Subscription') NOT NULL
);

CREATE TABLE Parking_Record (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    LicensePlate VARCHAR(15) NOT NULL,
    SpaceID INT NOT NULL,
    PaymentID INT NULL, -- FK added later
    EntryTime TIMESTAMP NOT NULL,
    ExitTime TIMESTAMP NULL,
    Duration INT NULL,
    FOREIGN KEY (LicensePlate) REFERENCES Vehicle(LicensePlate) ON DELETE RESTRICT,
    FOREIGN KEY (SpaceID) REFERENCES Parking_Space(SpaceID) ON DELETE RESTRICT,
    UNIQUE (PaymentID)
);

-- ===================================================================================
-- 4. LATE-BINDING FOREIGN KEYS (For circular dependencies)
-- ===================================================================================

ALTER TABLE Employee
ADD CONSTRAINT fk_manager
FOREIGN KEY (ManagerID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL;

ALTER TABLE Payment
ADD CONSTRAINT fk_payment_record
FOREIGN KEY (RecordID) REFERENCES Parking_Record(RecordID) ON DELETE RESTRICT;

ALTER TABLE Parking_Record
ADD CONSTRAINT fk_record_payment
FOREIGN KEY (PaymentID) REFERENCES Payment(PaymentID) ON DELETE RESTRICT;

-- Re-enable checks
SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Schema created successfully.' AS Status;
