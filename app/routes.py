from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from functools import wraps
from . import db_connector
import io
import csv

bp = Blueprint('bp', __name__)

# ---------------------------------------------------------------------
# Login required decorator
# ---------------------------------------------------------------------

def login_required(view):
    """Ensure that user is logged in before accessing a route."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'employee_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('bp.login'))
        return view(**kwargs)
    return wrapped_view

# --- Define allowed roles ---
MANAGER_ROLES = ['Admin', 'Manager', 'Supervisor']

def admin_required(view):
    """Ensure user is a manager or admin."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get('role') not in MANAGER_ROLES:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('bp.dashboard'))
        return view(**kwargs)
    return wrapped_view

# ---------------------------------------------------------------------
# Authentication routes
# ---------------------------------------------------------------------

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Employee login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        auth_result = db_connector.authenticate_user(username, password)
        if auth_result.get('status') == 'success':
            session['employee_id'] = auth_result.get('employee_id')
            session['username'] = username
            session['role'] = auth_result.get('role')
            flash(f"Logged in successfully as {username}.", 'success')
            return redirect(url_for('bp.dashboard'))
        else:
            flash(auth_result.get('message'), 'danger')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Logout the current user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('bp.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle new user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, username, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('bp.signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('bp.signup'))
        
        # Call the new register function
        reg_result = db_connector.register_user(name, username, password)
        
        if reg_result.get('status') == 'success':
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('bp.login'))
        else:
            flash(reg_result.get('message'), 'danger')
            return redirect(url_for('bp.signup'))

    # For GET request, just show the signup page
    return render_template('signup.html')

# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------

@bp.route('/dashboard')
@login_required
def dashboard():
    """Display real-time and financial summaries."""
    occupancy_data = db_connector.get_real_time_occupancy_report()
    financial_data = db_connector.get_financial_report()
    # vacant_spaces_data = db_connector.get_vacant_space_list()
    all_spaces_data = db_connector.get_all_parking_spaces()

    occupancy = occupancy_data.get('data') if occupancy_data.get('status') == 'success' else None
    financial_report = financial_data.get('data') if financial_data.get('status') == 'success' else None
    all_spaces = all_spaces_data.get('data') if all_spaces_data.get('status') == 'success' else []

    return render_template(
        'dashboard.html', 
        occupancy=occupancy, 
        financial_report=financial_report,
        all_spaces=all_spaces
        )

# ---------------------------------------------------------------------
# Operations Page
# ---------------------------------------------------------------------

@bp.route('/operations')
@login_required
def operations():
    """Render the parking operations page."""
    return render_template('operations.html')

# ---------------------------------------------------------------------
# Parking Operations
# ---------------------------------------------------------------------

@bp.route('/process_entry', methods=['POST'])
@login_required
def process_entry_route():
    """Handle vehicle entry."""
    license_plate = request.form.get('license_plate')
    space_id = request.form.get('space_id')

    result = db_connector.process_vehicle_entry(license_plate, space_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.operations'))


@bp.route('/process_exit', methods=['POST'])
@login_required
def process_exit_route():
    """Handle vehicle exit."""
    license_plate = request.form.get('license_plate')
    payment_method = request.form.get('payment_method')

    result = db_connector.process_vehicle_exit(license_plate,payment_method)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.operations'))


# @bp.route('/book_reservation', methods=['POST'])
# @login_required
# def book_reservation_route():
#     """Handle reservation booking."""
#     customer_id = request.form.get('customer_id')
#     space_id = request.form.get('space_id')

#     result = db_connector.book_reservation(customer_id, space_id)
#     flash(result.get('message'), result.get('status'))
#     return redirect(url_for('bp.operations'))

@bp.route('/book_reservation', methods=['POST'])
@login_required
def book_reservation_route():
    """Handle reservation form submission."""
    customer_id = request.form.get('customer_id')
    space_id = request.form.get('space_id')
    employee_id = session.get('employee_id')  # Logged-in user acts as employee

    result = db_connector.book_reservation(customer_id, space_id, employee_id)
    flash(result['message'], result['status'])
    return redirect(url_for('bp.operations'))


# ---------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------

@bp.route('/reports/hierarchy')
@login_required
def employee_hierarchy():
    """Displays Employee Hierarchy report."""
    report_data = db_connector.get_employee_hierarchy_report()
    hierarchy = report_data.get('data') if report_data.get('status') == 'success' else None
    return render_template('hierarchy_report.html', employees=hierarchy)

@bp.route('/reports/maintenance')
@login_required
def maintenance_audit():
    """Displays Maintenance Audit report."""
    report_data = db_connector.get_maintenance_audit_report()
    maintenance_logs = report_data.get('data') if report_data.get('status') == 'success' else []
    return render_template('maintenance_report.html', maintenance_logs=maintenance_logs)# Add this in the 'Reports' section of db_connector.py


@bp.route('/add_maintenance_log', methods=['POST'])
@login_required
def add_maintenance_log_route():
    """Handle the add new maintenance log form."""
    try:
        space_id = int(request.form.get('space_id'))
        cost = float(request.form.get('cost'))
    except (ValueError, TypeError):
        flash('Space ID and Cost must be valid numbers.', 'danger')
        return redirect(url_for('bp.maintenance_audit'))
        
    description = request.form.get('description')
    
    if not description:
        flash('Description is required.', 'danger')
        return redirect(url_for('bp.maintenance_audit'))

    result = db_connector.create_maintenance_log(space_id, description, cost)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.maintenance_audit'))

@bp.route('/complete_maintenance', methods=['POST'])
@login_required
def complete_maintenance_route():
    """Handle the complete maintenance button."""
    try:
        space_id = int(request.form.get('space_id'))
    except (ValueError, TypeError):
        flash('Invalid Space ID.', 'danger')
        return redirect(url_for('bp.maintenance_audit'))
        
    result = db_connector.complete_maintenance(space_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.maintenance_audit'))


# ---------------------------------------------------------------------
# Manager Reports & Exports
# ---------------------------------------------------------------------

@bp.route('/reports')
@login_required
@admin_required  # <-- Use the new decorator
def reports():
    """Display the main reports page for managers."""
    cust_data = db_connector.get_all_customers_report()
    veh_data = db_connector.get_all_vehicles_report()
    
    customers = cust_data.get('data') if cust_data.get('status') == 'success' else []
    vehicles = veh_data.get('data') if veh_data.get('status') == 'success' else []

    return render_template('reports.html', customers=customers, vehicles=vehicles)

@bp.route('/export/customers_csv')
@login_required
@admin_required
def export_customers_csv():
    """Export the customer list as a CSV file."""
    cust_data = db_connector.get_all_customers_report()
    if cust_data.get('status') != 'success':
        flash('Could not retrieve data for export.', 'danger')
        return redirect(url_for('bp.reports'))

    data = cust_data.get('data')
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write Header
    if data:
        cw.writerow(data[0].keys())
        # Write Data
        for row in data:
            cw.writerow(row.values())
    
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@bp.route('/export/vehicles_csv')
@login_required
@admin_required
def export_vehicles_csv():
    """Export the vehicle list as a CSV file."""
    veh_data = db_connector.get_all_vehicles_report()
    if veh_data.get('status') != 'success':
        flash('Could not retrieve data for export.', 'danger')
        return redirect(url_for('bp.reports'))

    data = veh_data.get('data')
    si = io.StringIO()
    cw = csv.writer(si)
    
    if data:
        cw.writerow(data[0].keys())
        for row in data:
            cw.writerow(row.values())
    
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=vehicles.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

# --- Add this new section to app/routes.py (near the other reports) ---

# ---------------------------------------------------------------------
# Management Page
# ---------------------------------------------------------------------

@bp.route('/management')
@login_required
def management():
    """Render the customer and vehicle management page."""
    # We could fetch lists of customers/vehicles here, but for now, just render
    services_data = db_connector.get_all_services()
    services = services_data.get('data') if services_data.get('status') == 'success' else []
    return render_template('management.html',services=services)


@bp.route('/add_customer', methods=['POST'])
@login_required
def add_customer_route():
    """Handle the add new customer form."""
    try:
        customer_id = int(request.form.get('customer_id'))
    except (ValueError, TypeError):
        flash('Customer ID must be a valid number.', 'danger')
        return redirect(url_for('bp.management'))
        
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip')
    
    if not name:
        flash('Customer Name is required.', 'danger')
        return redirect(url_for('bp.management'))

    result = db_connector.add_customer(customer_id, name, phone, email, street, city, state, zip_code)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))


@bp.route('/add_vehicle', methods=['POST'])
@login_required
def add_vehicle_route():
    """Handle the add new vehicle form."""
    license_plate = request.form.get('license_plate')
    try:
        customer_id = int(request.form.get('customer_id_vehicle'))
    except (ValueError, TypeError):
        flash('Customer ID must be a valid number.', 'danger')
        return redirect(url_for('bp.management'))

    make = request.form.get('make')
    model = request.form.get('model')
    color = request.form.get('color')

    if not license_plate:
        flash('License Plate is required.', 'danger')
        return redirect(url_for('bp.management'))

    result = db_connector.add_vehicle(license_plate, customer_id, make, model, color)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))


@bp.route('/assign_service', methods=['POST'])
@login_required
def assign_service_route():
    """Handle the assign service to customer form."""
    try:
        customer_id = int(request.form.get('customer_id_service'))
        service_id = int(request.form.get('service_id'))
    except (ValueError, TypeError):
        flash('Customer ID and Service ID must be valid numbers.', 'danger')
        return redirect(url_for('bp.management'))

    result = db_connector.assign_service_to_customer(customer_id, service_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))



# ---------------------------------------------------------------------
# Customer History API
# ---------------------------------------------------------------------

@bp.route('/api/customer_history/<int:customer_id>', methods=['GET'])
@login_required
def get_customer_history_api(customer_id):
    """Provide customer history as JSON API."""
    report_data = db_connector.get_customer_history(customer_id)
    if report_data.get('status') == 'success':
        return jsonify(report_data.get('data'))
    return jsonify({'error': report_data.get('message')}), 400


@bp.route('/add_service', methods=['POST'])
@login_required
def add_service_route():
    """Handle the add new service form."""
    name = request.form.get('service_name')
    description = request.form.get('service_description')
    try:
        cost = float(request.form.get('service_cost'))
    except (ValueError, TypeError):
        flash('Cost must be a valid number.', 'danger')
        return redirect(url_for('bp.management'))
    
    if not name:
        flash('Service Name is required.', 'danger')
        return redirect(url_for('bp.management'))

    result = db_connector.add_service(name, description, cost)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))


@bp.route('/api/service/<int:service_id>', methods=['GET'])
@login_required
def get_service_api(service_id):
    """Provide service details as JSON API for the edit modal."""
    result = db_connector.get_service_by_id(service_id)
    if result.get('status') == 'success':
        return jsonify(result.get('data'))
    return jsonify({'error': result.get('message')}), 404


@bp.route('/update_service', methods=['POST'])
@login_required
def update_service_route():
    """Handle the update service form from the modal."""
    try:
        service_id = int(request.form.get('edit_service_id'))
        cost = float(request.form.get('edit_service_cost'))
    except (ValueError, TypeError):
        flash('Invalid data submitted.', 'danger')
        return redirect(url_for('bp.management'))
        
    name = request.form.get('edit_service_name')
    description = request.form.get('edit_service_description')
    
    result = db_connector.update_service(service_id, name, description, cost)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))


@bp.route('/delete_service', methods=['POST'])
@login_required
def delete_service_route():
    """Handle the delete service action."""
    try:
        service_id = int(request.form.get('service_id'))
    except (ValueError, TypeError):
        flash('Invalid Service ID.', 'danger')
        return redirect(url_for('bp.management'))
        
    result = db_connector.delete_service(service_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.management'))




# ---------------------------------------------------------------------
# Edit &  Delete Options 
# ---------------------------------------------------------------------

@bp.route('/api/customer/<int:customer_id>', methods=['GET'])
@login_required
@admin_required
def get_customer_api(customer_id):
    """Provide customer details as JSON API for the edit modal."""
    result = db_connector.get_customer_by_id(customer_id)
    if result.get('status') == 'success':
        return jsonify(result.get('data'))
    return jsonify({'error': result.get('message')}), 404


@bp.route('/update_customer', methods=['POST'])
@login_required
@admin_required
def update_customer_route():
    """Handle the update customer form from the modal."""
    try:
        customer_id = int(request.form.get('edit_customer_id'))
    except (ValueError, TypeError):
        flash('Invalid Customer ID.', 'danger')
        return redirect(url_for('bp.reports'))
        
    name = request.form.get('edit_name')
    phone = request.form.get('edit_phone')
    email = request.form.get('edit_email')
    street = request.form.get('edit_street')
    city = request.form.get('edit_city')
    state = request.form.get('edit_state')
    zip_code = request.form.get('edit_zip')
    
    result = db_connector.update_customer(customer_id, name, phone, email, street, city, state, zip_code)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.reports'))


@bp.route('/delete_customer', methods=['POST'])
@login_required
@admin_required
def delete_customer_route():
    """Handle the delete customer action."""
    try:
        customer_id = int(request.form.get('customer_id'))
    except (ValueError, TypeError):
        flash('Invalid Customer ID.', 'danger')
        return redirect(url_for('bp.reports'))
        
    result = db_connector.delete_customer(customer_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.reports'))


# ---------------------------------------------------------------------
# Parking Lot Management
# ---------------------------------------------------------------------

@bp.route('/lots')
@login_required
@admin_required
def parking_lots():
    """Display the parking lot management page."""
    lots_data = db_connector.get_all_parking_lots()
    lots = lots_data.get('data') if lots_data.get('status') == 'success' else []
    return render_template('parking_lots.html', parking_lots=lots)

@bp.route('/api/lot/<int:lot_id>', methods=['GET'])
@login_required
@admin_required
def get_lot_api(lot_id):
    """Provide lot details as JSON API for the edit modal."""
    result = db_connector.get_lot_by_id(lot_id)
    if result.get('status') == 'success':
        return jsonify(result.get('data'))
    return jsonify({'error': result.get('message')}), 404

@bp.route('/add_lot', methods=['POST'])
@login_required
@admin_required
def add_lot_route():
    """Handle the add new lot form."""
    try:
        lot_id = int(request.form.get('lot_id'))
        total_spaces = int(request.form.get('total_spaces'))
    except (ValueError, TypeError):
        flash('Lot ID and Total Spaces must be valid numbers.', 'danger')
        return redirect(url_for('bp.parking_lots'))
        
    name = request.form.get('name')
    address = request.form.get('address')
    
    result = db_connector.add_parking_lot(lot_id, name, total_spaces, address)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.parking_lots'))

@bp.route('/update_lot', methods=['POST'])
@login_required
@admin_required
def update_lot_route():
    """Handle the update lot form from the modal."""
    try:
        lot_id = int(request.form.get('edit_lot_id'))
        total_spaces = int(request.form.get('edit_total_spaces'))
    except (ValueError, TypeError):
        flash('Invalid data submitted.', 'danger')
        return redirect(url_for('bp.parking_lots'))
        
    name = request.form.get('edit_name')
    address = request.form.get('edit_address')
    
    result = db_connector.update_parking_lot(lot_id, name, total_spaces, address)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.parking_lots'))

@bp.route('/delete_lot', methods=['POST'])
@login_required
@admin_required
def delete_lot_route():
    """Handle the delete lot action."""
    try:
        lot_id = int(request.form.get('lot_id'))
    except (ValueError, TypeError):
        flash('Invalid Lot ID.', 'danger')
        return redirect(url_for('bp.parking_lots'))
        
    result = db_connector.delete_parking_lot(lot_id)
    flash(result.get('message'), result.get('status'))
    return redirect(url_for('bp.parking_lots'))