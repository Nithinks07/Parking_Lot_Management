import mysql.connector
from mysql.connector import Error
from flask import current_app, g

def init_app(app):
    """Initializes app for database use (Flask context)."""
    app.teardown_appcontext(close_db)

def get_db():
    """Establish or reuse a MySQL connection."""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
            g.cursor = g.db.cursor(dictionary=True)
        except Error as e:
            print(f"Database connection failed: {e}")
            return None, None
    return g.db, g.cursor

def close_db(e=None):
    """Close the database connection at the end of request."""
    db = g.pop('db', None)
    cursor = g.pop('cursor', None)
    if cursor:
        cursor.close()
    if db:
        db.close()

# ---------------------------------------------------------------------
# Authentication & Procedures
# ---------------------------------------------------------------------

def authenticate_user(username, password):
    """Authenticate employee using stored procedure."""
    db, cursor = get_db()
    if not db:
        return {"status": "error", "message": "Database connection failed."}

    try:
        cursor.callproc('AuthenticateUser', (username, password))
        cursor.execute("SELECT @current_user_employee_id;")
        result = cursor.fetchone()
        employee_id = result.get('@current_user_employee_id')

        if employee_id:
            # Fetch the user's role
            cursor.execute("SELECT Role FROM Employee WHERE EmployeeID = %s", (employee_id,))
            employee_role = cursor.fetchone()
            role = employee_role.get('Role') if employee_role else 'Attendant' # Default fallback

            return {"status": "success", "employee_id": employee_id, "role": role}
        return {"status": "error", "message": "Invalid credentials or unauthorized user."}
    except Error as e:
        return {"status": "error", "message": str(e)}
    
def register_user(name, username, password):
    """Register a new employee and user."""
    db, cursor = get_db()
    if not db:
        return {"status": "error", "message": "Database connection failed."}

    try:
        # The trigger hashes the password, so we pass it plain
        cursor.callproc('CreateUserAndEmployee', (name, username, password))
        db.commit()
        
        # Fetch the result from the procedure
        for result in cursor.stored_results():
            reg_result = result.fetchone()

        if reg_result:
            return {"status": "success", "message": "Registration successful!", "employee_id": reg_result['NewEmployeeID']}
        else:
            return {"status": "error", "message": "Registration failed."}

    except Error as e:
        db.rollback()
        # Specific error for duplicate username
        if "Username already exists" in str(e):
            return {"status": "error", "message": "Username already exists. Please choose another."}
        return {"status": "error", "message": str(e)}

# ---------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------

def get_real_time_occupancy_report():
    """Fetch real-time parking space occupancy summary."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
            SELECT
                COUNT(SpaceID) AS TotalSpaces,
                SUM(CASE WHEN Status = 'Occupied' THEN 1 ELSE 0 END) AS OccupiedCount,
                SUM(CASE WHEN Status = 'Reserved' THEN 1 ELSE 0 END) AS ReservedCount,
                SUM(CASE WHEN Status = 'Vacant' THEN 1 ELSE 0 END) AS VacantCount
            FROM Parking_Space;
        """
        cursor.execute(query)
        data = cursor.fetchone()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def get_financial_report():
    """Generate financial summary grouped by payment method."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
            SELECT
                Method,
                COUNT(PaymentID) AS TotalTransactions,
                SUM(Amount) AS TotalRevenue
            FROM Payment
            WHERE Method IS NOT NULL
            GROUP BY Method
            ORDER BY TotalRevenue DESC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def get_employee_hierarchy_report():
    """Fetch employee-manager relationship report."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
            SELECT 
                e.EmployeeID,
                e.Name AS EmployeeName,
                e.Role,
                m.Name AS ManagerName
            FROM Employee e
            LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
            ORDER BY e.Role, e.Name;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}


# --- REPLACE your old get_maintenance_audit_report function ---
def get_maintenance_audit_report():
    """Retrieve all logs AND all spaces currently under maintenance."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        # This new query gets all spaces with logs AND spaces marked 'Maintenance'
        query = """
            SELECT 
                ps.SpaceID, 
                ps.SpaceNumber,
                ps.Status,
                ml.LogID, 
                ml.Description, 
                COALESCE(ml.Cost, 0) AS Cost, 
                ml.Maintenance_data
            FROM Parking_Space ps
            LEFT JOIN Maintenance_Log ml ON ps.SpaceID = ml.SpaceID
            WHERE ps.Status = 'Maintenance' OR ml.LogID IS NOT NULL
            ORDER BY ps.Status DESC, ml.Maintenance_data DESC, ps.SpaceNumber;
        """
        cursor.execute(query)
        data = cursor.fetchall() or []
        return {'status': 'success', 'data': data}

    except Error as e:
        return {'status': 'error', 'message': str(e)}

# --- ADD these two new functions at the end of the file ---
def create_maintenance_log(space_id, description, cost):
    """Call stored procedure to create a new maintenance log."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('CreateMaintenanceLog', (space_id, description, cost))
        db.commit()
        return {'status': 'success', 'message': 'Maintenance log created.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def complete_maintenance(space_id):
    """Call stored procedure to set space to vacant."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('CompleteMaintenance', (space_id,))
        db.commit()
        return {'status': 'success', 'message': 'Space set to Vacant.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def get_customer_history(customer_id):
    """Fetch full parking history for a given customer (based on Step 9 demo query)."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
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
            WHERE C.CustomerID = %s
            ORDER BY PR.EntryTime DESC;
        """
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        return {'status': 'success', 'data': results}
    except Error as e:
        return {'status': 'error', 'message': str(e)}
    
def get_vacant_space_list():
    """Fetch a list of all vacant parking spaces."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
            SELECT SpaceID, SpaceNumber
            FROM Parking_Space
            WHERE Status = 'Vacant'
            ORDER BY SpaceNumber;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}
    

def get_all_parking_spaces():
    """Fetch all parking spaces with their details."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        query = """
            SELECT SpaceID, SpaceNumber, SpaceType, Status
            FROM Parking_Space
            ORDER BY SpaceNumber;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}
    

# Add this in the 'Reports' section of db_connector.py

def get_all_customers_report():
    """Fetch all customers for the report."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        query = "SELECT CustomerID, Name, Phone, Email, PaymentCount FROM Customer ORDER BY Name;"
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def get_all_vehicles_report():
    """Fetch all vehicles with their owner's name for the report."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        query = """
            SELECT v.LicensePlate, v.Make, v.Model, v.Color, v.CustomerID, c.Name AS CustomerName
            FROM Vehicle v
            JOIN Customer c ON v.CustomerID = c.CustomerID
            ORDER BY c.Name, v.LicensePlate;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}



# ---------------------------------------------------------------------
# Parking Operations (Entry / Exit / Reservation)
# ---------------------------------------------------------------------

def process_vehicle_entry(license_plate, space_id):
    """Record a new vehicle entry (auto-link to a valid customer or reservation)."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        # ✅ Ensure the walk-in customer (ID=9999) exists and use it by default
        cursor.execute("SELECT CustomerID FROM Customer WHERE CustomerID = 9999;")
        walkin = cursor.fetchone()

        if not walkin:
            cursor.execute("""
                INSERT INTO Customer (CustomerID, Name, Phone, Email, Street, City, State, ZIP)
                VALUES (9999, 'Walk-in Customer', 'N/A', 'walkin@demo.com', 'N/A', 'N/A', 'N/A', '000000');
            """)
            customer_id = 9999
        else:
            customer_id = 9999


        # ✅ Ensure the vehicle exists
        cursor.execute("SELECT LicensePlate, CustomerID FROM Vehicle WHERE LicensePlate = %s", (license_plate,))
        vehicle = cursor.fetchone()
        if not vehicle:
            cursor.execute("""
                INSERT INTO Vehicle (LicensePlate, CustomerID, Make, Model, Color)
                VALUES (%s, %s, 'Walk-In', 'Unspecified', 'Unknown');
            """, (license_plate, customer_id))
        else:
            customer_id = vehicle['CustomerID']

        # ✅ Check space status
        cursor.execute("SELECT Status FROM Parking_Space WHERE SpaceID = %s", (space_id,))
        space = cursor.fetchone()
        if not space:
            return {'status': 'error', 'message': f"Invalid space ID {space_id}."}

        space_status = space['Status']

        # ✅ Handle space status
        if space_status == 'Vacant':
            pass  # normal entry allowed

        elif space_status == 'Reserved':
            # check if reservation belongs to this license plate
            cursor.execute("""
                SELECT * FROM Books 
                WHERE SpaceID = %s AND CustomerID = (
                    SELECT CustomerID FROM Vehicle WHERE LicensePlate = %s
                )
            """, (space_id, license_plate))
            reservation = cursor.fetchone()
            if not reservation:
                return {'status': 'error', 'message': f"Space {space_id} is reserved for another customer."}

        else:
            return {'status': 'error', 'message': f"Space {space_id} is not available (currently {space_status})."}

        # ✅ Insert parking record
        cursor.execute("""
            INSERT INTO Parking_Record (LicensePlate, EntryTime, SpaceID)
            VALUES (%s, NOW(), %s);
        """, (license_plate, space_id))

        # ✅ Update space status
        cursor.execute("UPDATE Parking_Space SET Status = 'Occupied' WHERE SpaceID = %s", (space_id,))

        # ✅ Optional: delete reservation after vehicle enters
        cursor.execute("""
            DELETE FROM Books 
            WHERE SpaceID = %s 
            AND CustomerID = (SELECT CustomerID FROM Vehicle WHERE LicensePlate = %s)
        """, (space_id, license_plate))

        db.commit()
        return {'status': 'success', 'message': f'Entry recorded successfully for {license_plate} at space {space_id}.'}

    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}




# --- REPLACE your old 'process_vehicle_exit' function with this: ---

def process_vehicle_exit(license_plate, payment_method):
    """Record a vehicle exit and create a payment record."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        # 1. Find the active record
        cursor.execute("""
            SELECT RecordID, SpaceID, EntryTime 
            FROM Parking_Record
            WHERE LicensePlate = %s AND ExitTime IS NULL
            ORDER BY EntryTime DESC LIMIT 1;
        """, (license_plate,))
        record = cursor.fetchone()
        if not record:
            return {'status': 'error', 'message': f'No active record found for {license_plate}.'}

        record_id = record['RecordID']
        space_id = record['SpaceID']
        entry_time = record['EntryTime']

        # 2. Calculate duration (in minutes)
        cursor.execute("SELECT TIMESTAMPDIFF(MINUTE, %s, NOW()) AS Duration", (entry_time,))
        duration = cursor.fetchone()['Duration']
        
        # Use the fee logic already in your file (₹50/hour)
        fee = round((duration / 60) * 50, 2) if duration else 0
        
        # 3. Start Transaction
        # db.start_transaction()

        # 4. Create Payment Record
        cursor.execute("""
            INSERT INTO Payment (RecordID, Amount, Timestamp, Method)
            VALUES (%s, %s, NOW(), %s);
        """, (record_id, fee, payment_method))
        
        payment_id = cursor.lastrowid

        # 5. Update Parking Record with ExitTime, Duration, and PaymentID
        cursor.execute("""
            UPDATE Parking_Record
            SET ExitTime = NOW(), Duration = %s, PaymentID = %s
            WHERE RecordID = %s;
        """, (duration, payment_id, record_id))

        # 6. Free up space
        cursor.execute("UPDATE Parking_Space SET Status = 'Vacant' WHERE SpaceID = %s", (space_id,))
        
        db.commit()

        # 7. Return a success message with all details
        return {'status': 'success', 'message': f'Exit & Payment successful for {license_plate}. Fee: ₹{fee:.2f} ({payment_method})'}
    
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}



def book_reservation(customer_id, space_id, employee_id, license_plate=None):
    """Reserve a parking space for a customer and optional vehicle."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        # Ensure customer exists
        cursor.execute("SELECT CustomerID FROM Customer WHERE CustomerID = %s", (customer_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO Customer (CustomerID, Name, Phone, Email, Street, City, State, ZIP)
                VALUES (%s, 'Walk-in Customer', 'N/A', CONCAT('auto_', %s, '@demo.com'), 'N/A', 'N/A', 'N/A', '000000');
            """, (customer_id, customer_id))

        # If license_plate is given, ensure vehicle exists
        if license_plate:
            cursor.execute("SELECT LicensePlate FROM Vehicle WHERE LicensePlate = %s", (license_plate,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Vehicle (LicensePlate, CustomerID, Make, Model, Color)
                    VALUES (%s, %s, 'Unknown', 'Unknown', 'Unknown');
                """, (license_plate, customer_id))

        # Check space availability
        cursor.execute("SELECT Status FROM Parking_Space WHERE SpaceID = %s", (space_id,))
        space = cursor.fetchone()
        if not space:
            return {'status': 'error', 'message': 'Invalid Space ID.'}
        if space['Status'] != 'Vacant':
            return {'status': 'error', 'message': f"Space {space_id} is not available."}

        # Insert reservation (with license plate if given)
        cursor.execute("""
            INSERT INTO Books (CustomerID, SpaceID, EmployeeID, LicensePlate, ReservationTime, Notes)
            VALUES (%s, %s, %s, %s, NOW(), 'Reserved via system');
        """, (customer_id, space_id, employee_id, license_plate))

        # Update space status
        cursor.execute("UPDATE Parking_Space SET Status = 'Reserved' WHERE SpaceID = %s", (space_id,))
        db.commit()

        return {'status': 'success', 'message': f'Space {space_id} reserved successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}



# --- Add this new section to app/db_connector.py ---

# ---------------------------------------------------------------------
# Customer & Vehicle Management
# ---------------------------------------------------------------------

def add_customer(customer_id, name, phone, email, street, city, state, zip_code):
    """Call stored procedure to add a new customer."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}

    try:
        # Handle empty strings vs NULL for optional fields
        phone = phone if phone else None
        email = email if email else None
        street = street if street else None
        city = city if city else None
        state = state if state else None
        zip_code = zip_code if zip_code else None

        cursor.callproc('AddCustomer', (customer_id, name, phone, email, street, city, state, zip_code))
        db.commit()
        return {'status': 'success', 'message': f'Customer {name} (ID: {customer_id}) added successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}


def add_vehicle(license_plate, customer_id, make, model, color):
    """Call stored procedure to add a new vehicle."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
        
    try:
        make = make if make else None
        model = model if model else None
        color = color if color else None

        cursor.callproc('AddVehicle', (license_plate, customer_id, make, model, color))
        db.commit()
        return {'status': 'success', 'message': f'Vehicle {license_plate} added successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}
    


def get_all_services():
    """Fetch a list of all available services."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        query = "SELECT ServiceID, Name, Description, Cost FROM Service ORDER BY ServiceID;"
        cursor.execute(query)
        data = cursor.fetchall()
        return {'status': 'success', 'data': data}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def assign_service_to_customer(customer_id, service_id):
    """Call stored procedure to assign a service to a customer."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
        
    try:
        cursor.callproc('AssignServiceToCustomer', (customer_id, service_id))
        db.commit()
        return {'status': 'success', 'message': 'Service assigned successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}
    

def add_service(name, description, cost):
    """Call stored procedure to add a new service."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('AddService', (name, description, cost))
        db.commit()
        return {'status': 'success', 'message': 'Service added successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def get_service_by_id(service_id):
    """Fetch a single service by its ID."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('GetServiceByID', (service_id,))
        for result in cursor.stored_results():
            service = result.fetchone()
        
        if service:
            return {'status': 'success', 'data': service}
        else:
            return {'status': 'error', 'message': 'Service not found.'}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def update_service(service_id, name, description, cost):
    """Call stored procedure to update a service."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('UpdateService', (service_id, name, description, cost))
        db.commit()
        return {'status': 'success', 'message': 'Service updated successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def delete_service(service_id):
    """Call stored procedure to delete a service."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('DeleteService', (service_id,))
        db.commit()
        return {'status': 'success', 'message': 'Service deleted successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}
    

def get_customer_by_id(customer_id):
   
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('GetCustomerByID', (customer_id,))
        for result in cursor.stored_results():
            customer = result.fetchone()
        
        if customer:
            return {'status': 'success', 'data': customer}
        else:
            return {'status': 'error', 'message': 'Customer not found.'}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def update_customer(customer_id, name, phone, email, street, city, state, zip_code):
    """Call stored procedure to update a customer."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('UpdateCustomer', (customer_id, name, phone, email, street, city, state, zip_code))
        db.commit()
        return {'status': 'success', 'message': 'Customer updated successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def delete_customer(customer_id):
    """Call stored procedure to delete a customer."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('DeleteCustomer', (customer_id,))
        db.commit()
        return {'status': 'success', 'message': 'Customer deleted successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}


# ---------------------------------------------------------------------
# Lot Management
# ---------------------------------------------------------------------

def get_all_parking_lots():
    """Fetch all parking lots."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('GetAllParkingLots')
        for result in cursor.stored_results():
            lots = result.fetchall()
        return {'status': 'success', 'data': lots}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def get_lot_by_id(lot_id):
    """Fetch a single lot by its ID."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('GetParkingLotByID', (lot_id,))
        for result in cursor.stored_results():
            lot = result.fetchone()
        
        if lot:
            return {'status': 'success', 'data': lot}
        else:
            return {'status': 'error', 'message': 'Lot not found.'}
    except Error as e:
        return {'status': 'error', 'message': str(e)}

def add_parking_lot(lot_id, name, total_spaces, address):
    """Call stored procedure to add a new lot."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('AddParkingLot', (lot_id, name, total_spaces, address))
        db.commit()
        return {'status': 'success', 'message': 'Parking lot added successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def update_parking_lot(lot_id, name, total_spaces, address):
    """Call stored procedure to update a lot."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('UpdateParkingLot', (lot_id, name, total_spaces, address))
        db.commit()
        return {'status': 'success', 'message': 'Parking lot updated successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}

def delete_parking_lot(lot_id):
    """Call stored procedure to delete a lot."""
    db, cursor = get_db()
    if not db:
        return {'status': 'error', 'message': 'Database connection failed.'}
    try:
        cursor.callproc('DeleteParkingLot', (lot_id,))
        db.commit()
        return {'status': 'success', 'message': 'Parking lot deleted successfully.'}
    except Error as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}