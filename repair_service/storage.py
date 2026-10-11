# Data storage module using standard JSON files and os

import os
import json
from tkinter import messagebox

# Determine the path to the data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
SERVICES_FILE = "services.json"
JOBS_FILE = "jobs.json"
PARTS_FILE = "parts.json"
PAYMENTS_FILE = "payments.json"


def get_file_path(filename):
    """Return full absolute path for a data file."""
    return os.path.join(DATA_DIR, filename)


def init_storage():
    """Ensure data directory and required data files exist with seed data."""
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Seed users if missing or empty
        users_path = get_file_path(USERS_FILE)
        if not os.path.exists(users_path) or os.path.getsize(users_path) == 0:
            default_users = [
                {
                    "user_id": "USR-001",
                    "username": "admin",
                    "password": "admin123",
                    "role": "Admin",
                    "full_name": "System Administrator",
                    "customer_id": ""
                },
                {
                    "user_id": "USR-002",
                    "username": "staff",
                    "password": "staff123",
                    "role": "Staff",
                    "full_name": "Front Desk Staff",
                    "customer_id": ""
                },
                {
                    "user_id": "USR-003",
                    "username": "tech1",
                    "password": "tech123",
                    "role": "Technician",
                    "full_name": "John Technician",
                    "customer_id": ""
                }
            ]
            save_data(USERS_FILE, default_users)

        # Seed services if missing or empty list
        if len(load_services()) == 0:
            default_services = [
                {"service_id": "SRV-001", "name": "Diagnostic", "description": "Full hardware and software diagnostic check", "price": 300.0},
                {"service_id": "SRV-002", "name": "OS Reinstallation", "description": "Clean install of Windows/Linux OS with drivers", "price": 500.0},
                {"service_id": "SRV-003", "name": "Virus Removal", "description": "Malware, spyware, and virus cleanup", "price": 400.0},
                {"service_id": "SRV-004", "name": "Screen Replacement", "description": "LCD/LED panel replacement labor", "price": 1500.0},
                {"service_id": "SRV-005", "name": "Battery Replacement", "description": "Laptop battery replacement labor", "price": 500.0},
                {"service_id": "SRV-006", "name": "Keyboard Replacement", "description": "Internal laptop keyboard replacement labor", "price": 800.0},
                {"service_id": "SRV-007", "name": "RAM/SSD Upgrade", "description": "Storage or memory installation and configuration", "price": 400.0},
                {"service_id": "SRV-008", "name": "Data Backup", "description": "User files backup and transfer to external storage", "price": 500.0},
                {"service_id": "SRV-009", "name": "Cleaning/Thermal Paste", "description": "Internal dust removal and CPU/GPU thermal paste re-application", "price": 450.0}
            ]
            save_data(SERVICES_FILE, default_services)

        # Seed parts if missing or empty list
        if len(load_parts()) == 0:
            default_parts = [
                {"part_id": "PRT-001", "name": "500GB NVMe SSD", "quantity": 8, "unit_price": 1800.0},
                {"part_id": "PRT-002", "name": "8GB DDR4 RAM", "quantity": 10, "unit_price": 1200.0},
                {"part_id": "PRT-003", "name": "Thermal Paste (Arctic MX-4)", "quantity": 15, "unit_price": 300.0},
                {"part_id": "PRT-004", "name": "15.6\" FHD Slim LED Screen", "quantity": 4, "unit_price": 3200.0},
                {"part_id": "PRT-005", "name": "Laptop Battery 45Wh", "quantity": 5, "unit_price": 1600.0},
                {"part_id": "PRT-006", "name": "Universal Keyboard", "quantity": 6, "unit_price": 850.0},
                {"part_id": "PRT-007", "name": "65W Laptop Charger", "quantity": 7, "unit_price": 750.0}
            ]
            save_data(PARTS_FILE, default_parts)

        # Initialize empty files if missing
        for filename in [CUSTOMERS_FILE, JOBS_FILE, PAYMENTS_FILE]:
            fpath = get_file_path(filename)
            if not os.path.exists(fpath):
                save_data(filename, [])

    except Exception as e:
        messagebox.showerror("Storage Error", f"Failed to initialize storage: {e}")


def backup_data():
    """Copy all data files into a backup folder (FR-50)."""
    import shutil
    from datetime import datetime

    backup_base = os.path.join(BASE_DIR, "backups")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_target = os.path.join(backup_base, f"backup_{timestamp}")

    try:
        if not os.path.exists(backup_target):
            os.makedirs(backup_target)

        for filename in [USERS_FILE, CUSTOMERS_FILE, SERVICES_FILE, JOBS_FILE, PARTS_FILE, PAYMENTS_FILE]:
            src = get_file_path(filename)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_target, filename))
        return backup_target
    except Exception as e:
        messagebox.showerror("Backup Error", f"Failed to create backup: {e}")
        return None


def load_data(filename):
    """Load JSON data from a file inside the data directory."""
    path = get_file_path(filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        messagebox.showerror("File Error", f"Data file {filename} is corrupted. An empty list will be used.")
        return []
    except Exception as e:
        messagebox.showerror("File Error", f"Unable to read {filename}: {e}")
        return []


def save_data(filename, data):
    """Save data to a JSON file inside the data directory."""
    path = get_file_path(filename)
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("File Error", f"Unable to save data to {filename}: {e}")
        return False


# Convenience helper functions
def load_users():
    users = load_data(USERS_FILE)
    for u in users:
        if "customer_id" not in u:
            u["customer_id"] = ""
    return users


def save_users(users):
    return save_data(USERS_FILE, users)


def load_customers():
    return load_data(CUSTOMERS_FILE)


def save_customers(customers):
    return save_data(CUSTOMERS_FILE, customers)


def load_services():
    return load_data(SERVICES_FILE)


def save_services(services):
    return save_data(SERVICES_FILE, services)


def load_jobs():
    jobs = load_data(JOBS_FILE)
    for j in jobs:
        if "source" not in j:
            j["source"] = "Walk-in"
        if "date_submitted" not in j:
            j["date_submitted"] = j.get("date_received", "")
        if "parts_used" not in j:
            j["parts_used"] = []
        if "services" not in j:
            j["services"] = []
        if "status_history" not in j:
            j["status_history"] = []
    return jobs


def save_jobs(jobs):
    return save_data(JOBS_FILE, jobs)


def load_parts():
    return load_data(PARTS_FILE)


def save_parts(parts):
    return save_data(PARTS_FILE, parts)


def load_payments():
    return load_data(PAYMENTS_FILE)


def save_payments(payments):
    return save_data(PAYMENTS_FILE, payments)
