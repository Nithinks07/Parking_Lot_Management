-- ===================================================================================
-- 04_ANALYTICAL_QUERIES.SQL
-- This file contains the analytical queries from your original demo script.
-- You can run this at any time to see a snapshot of your application's data.
-- ===================================================================================

USE plm;

-- 1. Real-Time Occupancy
SELECT '--- 1. REAL-TIME OCCUPANCY REPORT ---' AS Report;
SELECT
    COUNT(SpaceID) AS TotalSpaces,
    SUM(CASE WHEN Status = 'Occupied' THEN 1 ELSE 0 END) AS OccupiedCount,
    SUM(CASE WHEN Status = 'Reserved' THEN 1 ELSE 0 END) AS ReservedCount,
    SUM(CASE WHEN Status = 'Vacant' THEN 1 ELSE 0 END) AS VacantCount,
    SUM(CASE WHEN Status = 'Maintenance' THEN 1 ELSE 0 END) AS MaintenanceCount
FROM Parking_Space;

-- 2. Financial Report
SELECT '--- 2. FINANCIAL REPORT (Revenue by Payment Method) ---' AS Report;
SELECT
    Method,
    COUNT(PaymentID) AS TotalTransactions,
    SUM(Amount) AS TotalRevenue
FROM Payment
WHERE Method IS NOT NULL
GROUP BY Method
ORDER BY TotalRevenue DESC;

-- 3. Customer History (Example: Customer 1001)
SELECT '--- 3. CUSTOMER HISTORY (Example: 1001) ---' AS Report;
SELECT
    C.Name AS CustomerName,
    V.LicensePlate,
    PR.EntryTime,
    PR.ExitTime,
    PR.Duration AS DurationMinutes,
    P.Amount AS FeePaid,
    P.Method
FROM Customer C
JOIN Vehicle V ON C.CustomerID = V.CustomerID
JOIN Parking_Record PR ON V.LicensePlate = PR.LicensePlate
LEFT JOIN Payment P ON PR.PaymentID = P.PaymentID
WHERE C.CustomerID = 1001
ORDER BY PR.EntryTime DESC;

-- 4. Hierarchy Check
SELECT '--- 4. EMPLOYEE MANAGEMENT HIERARCHY (Self-Join) ---' AS Report;
SELECT
    e.EmployeeID,
    e.Name AS EmployeeName,
    e.Role,
    m.Name AS ManagerName
FROM Employee e
LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID;

-- 5. Maintenance Audit
SELECT '--- 5. MAINTENANCE AUDIT ---' AS Report;
SELECT
    PS.SpaceID,
    PS.SpaceNumber,
    PS.Status,
    ML.LogID,
    ML.Description,
    ML.Cost,
    ML.Maintenance_data
FROM Maintenance_Log ML
JOIN Parking_Space PS ON ML.SpaceID = PS.SpaceID
ORDER BY PS.SpaceID, ML.LogID;

SELECT '--- QUERIES COMPLETE ---' AS Status;
