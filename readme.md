# 🚗 PLM Automated Parking Management System

A **full-stack web application** built with **Flask** and **MySQL** to manage a multi-level parking facility.  
This system provides a complete solution for operators — from real-time vehicle entry/exit processing to high-level administrative management and reporting.

---

<img width="939" height="528" alt="image" src="https://github.com/user-attachments/assets/57f5f420-b128-4014-9c03-cb1d6d509fe5" />
<img width="895" height="503" alt="image" src="https://github.com/user-attachments/assets/776111d3-f6b1-424c-9442-bc232026b192" />
<img width="931" height="524" alt="image" src="https://github.com/user-attachments/assets/2cd2de1c-23bf-4aa0-86e7-a737cd62d211" />
<img width="888" height="499" alt="image" src="https://github.com/user-attachments/assets/db24f5fc-7075-4f68-b8cf-9d6edf4d78e2" />



## 🌟 Key Features

The application is organized into modules based on **user roles and responsibilities**.

### ⚙️ Core Operations
- **Vehicle Entry**: Register new or existing vehicles as they enter the lot.  
- **Vehicle Exit**: Process vehicle exits, automatically calculate fees, and record payments.  
- **Reservations**: Book specific parking spaces for registered customers.

### 📊 Real-time Dashboard
- **Occupancy Stats**: Live-updating cards (Total, Occupied, Reserved, Vacant).  
- **Occupancy Chart**: Doughnut chart visualizing the current lot status.  
- **Financial Report**: Revenue summary grouped by payment method.  
- **Full Space Status**: Detailed, scrollable table of all parking spaces with live statuses and quick actions.

### 🧑‍💼 Management Suite
- **Customer Management**: Add and edit customer profiles.  
- **Vehicle Management**: Add new vehicles and link them to customers.  
- **Service Management**: Add, edit, and assign services (e.g., *EV Charging*, *Car Wash*) to customers.

### 🔐 Admin & Reporting
- **Role-Based Access Control**: Restricts access by role — *Admin, Manager, Supervisor, Attendant*.  
- **Manager Reports**: View sortable lists of all customers and vehicles.  
- **CSV Export**: Download customer and vehicle lists.  
- **CRUD Modals**: Edit or delete records directly from management pages.

### 🛠️ Maintenance Module
- **Create Logs**: Attendants can log maintenance tasks (auto-sets space status to *Maintenance*).  
- **Complete Logs**: Mark tasks as complete to restore *Vacant* status.

### 🏢 Lot Administration (Admin Only)
- **Multi-Lot Support**: Designed to manage multiple parking lots.  
- **Lot Management**: Secure admin tools to add, edit, or delete lots.

---

## 🧰 Technology Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Python (Flask) |
| **Database** | MySQL |
| **Frontend** | HTML5, Tailwind CSS, Chart.js, Font Awesome |
| **Server** | Werkzeug |
| **Environment** | python-dotenv |

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1️⃣ Prerequisites
Ensure you have the following installed:
- Python **3.10+**
- MySQL Server
- Git

---

### 2️⃣ Database Setup

Set up the database before starting the app:

1. Open your MySQL client (Workbench / terminal).
2. Run the following SQL scripts **in order** from the `database/` folder:
   ```bash
   01_create_schema.sql       # Creates database and tables
   02_create_logic.sql        # Creates procedures, triggers, and functions
   03_insert_base_data.sql    # Inserts essential data
   ```

---

### 3️⃣ Local Installation

Follow these steps to run the project on your local machine.

#### 🧩 Step 1: Clone the Repository
```bash
git clone https://github.com/Nithinks07/PLM-Parking-System.git
cd PLM-Parking-System
```

#### 🧱 Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.
env\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### ⚙️ Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### 🔑 Step 4: Set Up Environment Variables
1. Create a new file named **.env** in the root folder.  
2. Copy contents from **.env.example**.  
3. Update your configuration — especially `DB_PASSWORD`, `DB_USER`, and `DB_NAME`.

Example:
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=plm_db
SECRET_KEY=your_secret_key
```

#### ▶️ Step 5: Run the Application
```bash
python run.py
```

Access it in your browser at:  
👉 http://127.0.0.1:5000/login

---

## 🗂️ Project Structure

```bash
PLM/
│
├── .env                 # Local secrets (ignored by Git)
├── .env.example         # Template for environment setup
├── .gitignore           # Files ignored by Git
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── run.py               # Application entry point
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── db_connector.py      # Database connection logic
│   ├── routes.py            # All Flask routes
│   │
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── ... (other .html files)
│   │   └── partials/        # Modal components
│   │       └── ...
│   │
│   └── static/              # Static assets
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── main.js
│
└── database/
    ├── 01_create_schema.sql
    ├── 02_create_logic.sql
    ├── 03_insert_base_data.sql
    ├── 04_analytical_queries.sql
    └── 05_reset_database.sql
```

---

## 💡 Future Enhancements
- 🚘 Integration with license plate recognition (LPR) cameras  
- 💳 Online booking and digital payments  
- 🛰️ IoT-based occupancy detection  
- 📱 Mobile app interface (React Native)

---

## 🧑‍💻 Authors
**1. Nithin K S**  
📍 PES University  
💻 GitHub: [@Nithinks07](https://github.com/Nithinks07)
**2. Nikhil P S**  
📍 PES University  
💻 GitHub: [@pes1ug23am191](https://github.com/pes1ug23am191)







