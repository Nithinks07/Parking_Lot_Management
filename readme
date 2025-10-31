# 🚗 PLM Automated Parking Management System

A full-stack web application built with **Flask** and **MySQL** to manage a multi-level parking facility.  
This system provides a complete solution for operators — from real-time vehicle entry/exit processing to high-level administrative management and reporting.

---

## 🌟 Key Features

### ⚙️ Core Operations
- **Vehicle Entry:** Register new or existing vehicles as they enter the lot.  
- **Vehicle Exit:** Process vehicle exits, automatically calculating fees and recording payments.  
- **Reservations:** Book specific parking spaces for registered customers.  

---

### 📊 Real-time Dashboard
- **Occupancy Stats:** Live-updating cards showing total, occupied, reserved, and vacant spaces.  
- **Occupancy Chart:** Doughnut chart visualizing the current lot status.  
- **Financial Report:** Revenue summary grouped by payment method.  
- **Full Space Status:** Scrollable table of all parking spaces with live status (Vacant, Occupied, Maintenance) and quick-action buttons.

---

### 🧑‍💼 Management Suite
- **Customer Management:** Add new customers with full contact details.  
- **Vehicle Management:** Add new vehicles and assign them to customers.  
- **Service Management:** Add, edit, and delete services (e.g., “EV Charging”, “Car Wash”) and assign them to specific customers.  

---

### 🔐 Admin & Reporting
- **Role-Based Access Control:** Differentiates between Admin, Manager, Supervisor, and Attendant roles.  
- **Manager Reports:** Sortable, full lists of all customers and vehicles.  
- **CSV Export:** Download complete customer and vehicle lists.  
- **CRUD Modals:** Edit or delete customers, vehicles, and services directly from the management pages.  

---

### 🛠️ Maintenance Module
- **Create Logs:** Attendants can create maintenance logs for specific spaces, setting their status to *Maintenance*.  
- **Complete Logs:** Mark maintenance complete to set the space status back to *Vacant*.  

---

### 🏢 Lot Administration (Admin Only)
- **Multi-Lot Support:** Database supports multiple parking lots.  
- **Lot Management:** Admins can add, edit, or delete entire lots securely.  

---

## 🛠️ Technology Stack
- **Backend:** Python (Flask)  
- **Database:** MySQL  
- **Frontend:** HTML5, Tailwind CSS, Chart.js, Font Awesome  
- **Server:** Werkzeug  
- **Environment:** python-dotenv  

---

## 🚀 Getting Started

Follow these steps to get a copy of the project running locally.

### 1️⃣ Prerequisites
- Python (3.10+)  
- MySQL Server  
- Git  

---

### 2️⃣ Database Setup

Set up the database before running the app:

1. Open your MySQL client (Workbench, terminal, etc.)  
2. Run the SQL files from the `database/` folder in **this order:**
   ```bash
   01_create_schema.sql      # Creates the database and tables
   02_create_logic.sql       # Creates procedures, functions, triggers
   03_insert_base_data.sql   # Inserts essential base data
