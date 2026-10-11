# Computer & Laptop Repair Service System
## Functional Requirements Specification

**Course:** IT Professional Elective 1 (ITEP310-T)
**Language / GUI:** Python 3 + Tkinter (desktop GUI, no terminal interaction)
**Storage:** Local files (CSV / JSON / TXT) using Python file I/O

---

## 1. Introduction

### 1.1 Purpose
This document lists what the Computer & Laptop Repair Service System must do. The system helps a repair shop record customers, receive devices for repair, assign technicians, track repair progress, and issue billing.

### 1.2 Scope
A standalone desktop application with a graphical interface. All interaction (input, buttons, tables, messages) happens through windows. The terminal is only used to launch the program.

### 1.3 Technical Constraints (based on the lesson)
| Constraint | Detail |
|---|---|
| GUI library | Tkinter (`tkinter`, `tkinter.messagebox`, `tkinter.ttk` for tables/combobox) |
| Data storage | File I/O (`open()`, `read()`, `write()`, `os` module) |
| Data structures | Lists, tuples, dictionaries for records |
| Error handling | `try / except / finally` on all file and input operations |
| Code organization | Functions + modules (e.g., `gui.py`, `storage.py`, `models.py`) |
| Python version | The lesson uses Python 2 syntax (`Tkinter`, `print x`). Use Python 3 equivalents (`tkinter`, `print(x)`) when coding. |

### 1.4 Definitions
| Term | Meaning |
|---|---|
| Job Order / Ticket | A repair request for one device |
| Technician | Staff who diagnoses and repairs devices |
| Service | A repair task with a fixed price (e.g., OS reinstall) |

---

## 2. User Roles

| Role | Description |
|---|---|
| **Admin** | Manages users, services, prices, and views all reports |
| **Front Desk / Staff** | Registers customers, creates job orders, processes payments, releases devices |
| **Technician** | Views assigned jobs, updates status, records diagnosis and parts used |

---

## 3. Functional Requirements

Priority: **M** = Must have, **S** = Should have, **C** = Could have (if time allows)

### 3.1 Authentication & User Management
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The system shall display a login window asking for username and password. | M |
| FR-02 | The system shall validate credentials against stored user records and show an error message on failure. | M |
| FR-03 | The system shall open a main menu based on the user's role (Admin, Staff, Technician). | M |
| FR-04 | The system shall mask the password field (`show="*"`). | M |
| FR-05 | Admin shall be able to add, edit, and delete user accounts. | S |
| FR-06 | The system shall provide a logout option that returns to the login window. | M |

### 3.2 Customer Management
| ID | Requirement | Priority |
|---|---|---|
| FR-07 | The system shall allow adding a customer with: Customer ID (auto-generated), full name, contact number, email, address. | M |
| FR-08 | The system shall allow editing customer details. | M |
| FR-09 | The system shall allow deleting a customer (blocked if the customer has an active job order). | S |
| FR-10 | The system shall display all customers in a table. | M |
| FR-11 | The system shall allow searching customers by name, ID, or contact number. | M |
| FR-12 | The system shall show a customer's repair history. | S |

### 3.3 Device & Job Order (Intake)
| ID | Requirement | Priority |
|---|---|---|
| FR-13 | The system shall create a job order with an auto-generated Job ID and the current date/time. | M |
| FR-14 | A job order shall record: customer, device type (Laptop / Desktop / All-in-One), brand, model, serial number, accessories received (charger, bag, etc.). | M |
| FR-15 | A job order shall record the customer's problem description. | M |
| FR-16 | A job order shall record the device's physical condition on arrival (scratches, cracks, etc.). | S |
| FR-17 | A job order shall record the priority level (Normal / Urgent). | S |
| FR-18 | The system shall record the estimated completion date. | S |
| FR-19 | The system shall generate a printable/viewable job receipt (text window or `.txt` file) for the customer. | S |
| FR-20 | The system shall prevent saving a job order if required fields are empty. | M |

### 3.4 Service Catalog & Pricing
| ID | Requirement | Priority |
|---|---|---|
| FR-21 | Admin shall add, edit, and delete services with: Service ID, name, description, price. | M |
| FR-22 | Sample services shall include: Diagnostic, OS Reinstallation, Virus Removal, Screen Replacement, Battery Replacement, Keyboard Replacement, Hardware Upgrade (RAM/SSD), Data Backup, Cleaning/Thermal Paste. | M |
| FR-23 | Services shall be selectable (Listbox/Combobox) and attachable to a job order. | M |
| FR-24 | A job order may contain multiple services. | M |

### 3.5 Technician Assignment & Repair Tracking
| ID | Requirement | Priority |
|---|---|---|
| FR-25 | Staff/Admin shall assign a technician to a job order. | M |
| FR-26 | Technicians shall see a list of jobs assigned to them. | M |
| FR-27 | Technicians shall record a diagnosis and repair notes per job. | M |
| FR-28 | The system shall support these statuses: **Received → Diagnosing → Waiting for Parts → Under Repair → Completed → Released** (and **Cancelled**). | M |
| FR-29 | The system shall record a timestamp every time the status changes. | S |
| FR-30 | The system shall display all job orders in a table, filterable by status. | M |
| FR-31 | The system shall search job orders by Job ID, customer name, or serial number. | M |
| FR-32 | Customers shall be notified of completion through an on-screen prompt for Staff to contact them (actual SMS/email is out of scope). | C |

### 3.6 Parts & Inventory (Optional Module)
| ID | Requirement | Priority |
|---|---|---|
| FR-33 | The system shall store parts with: Part ID, name, quantity, unit price. | S |
| FR-34 | Technicians shall add parts used to a job order; stock shall decrease automatically. | S |
| FR-35 | The system shall warn when a part's stock is at or below a set threshold. | C |
| FR-36 | The system shall block adding a part if stock is insufficient. | S |

### 3.7 Billing & Payment
| ID | Requirement | Priority |
|---|---|---|
| FR-37 | The system shall compute the total = sum of services + parts used. | M |
| FR-38 | The system shall allow recording a down payment/deposit. | S |
| FR-39 | The system shall record payment: amount, method (Cash / GCash / Card), date. | M |
| FR-40 | The system shall compute the remaining balance and change. | M |
| FR-41 | The system shall generate an official receipt/invoice (text window or `.txt` file). | M |
| FR-42 | A device shall only be marked **Released** after the balance is fully paid. | M |

### 3.8 Reports
| ID | Requirement | Priority |
|---|---|---|
| FR-43 | The system shall show a dashboard with counts per status (e.g., Received: 3, Under Repair: 5). | S |
| FR-44 | The system shall generate a daily/monthly sales report. | S |
| FR-45 | The system shall list pending (unfinished) jobs. | S |
| FR-46 | Reports shall be exportable to a `.txt` or `.csv` file. | C |

### 3.9 Data Management
| ID | Requirement | Priority |
|---|---|---|
| FR-47 | The system shall save all records (users, customers, jobs, services, parts, payments) to local files. | M |
| FR-48 | The system shall load saved records automatically on startup. | M |
| FR-49 | The system shall create the data files/folders automatically if they do not exist (`os.path`, `os.mkdir`). | M |
| FR-50 | The system shall provide a backup option that copies data files to a backup folder. | C |

### 3.10 Validation & Error Handling
| ID | Requirement | Priority |
|---|---|---|
| FR-51 | The system shall validate inputs: required fields, numeric-only for contact number/price/quantity, valid email format, valid dates. | M |
| FR-52 | The system shall show errors through message boxes (`showerror`, `showwarning`, `showinfo`) instead of terminal output. | M |
| FR-53 | The system shall ask for confirmation before deleting or cancelling a record (`askyesno`). | M |
| FR-54 | The system shall handle file errors (missing/corrupted file, no permission) using `try/except` without crashing. | M |
| FR-55 | The system shall prevent duplicate IDs. | M |

### 3.11 GUI Requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-56 | All features shall be operated through a Tkinter GUI; no `input()` or terminal prompts. | M |
| FR-57 | The main window shall have a menu bar or button panel: Customers, Job Orders, Services, Parts, Billing, Reports, Logout. | M |
| FR-58 | Forms shall use appropriate widgets (see table below). | M |
| FR-59 | Record lists shall be shown in a table (`ttk.Treeview`) with a scrollbar. | M |
| FR-60 | The interface shall use consistent layout, labels, and button names across all windows. | S |

**Widget mapping**

| Need | Tkinter widget |
|---|---|
| Text input (name, serial no.) | `Entry` |
| Long text (problem, diagnosis) | `Text` |
| Choose one (device type, payment method) | `Radiobutton` / `ttk.Combobox` |
| Choose many (accessories received) | `Checkbutton` |
| Pick a service | `Listbox` / `Combobox` |
| Number input (quantity) | `Spinbox` |
| Group form sections | `Frame` / `LabelFrame` |
| Static text | `Label` |
| Actions (Save, Delete, Search) | `Button` |
| Pop-up forms / receipts | `Toplevel` |
| Alerts and confirmations | `messagebox` |
| Record tables | `ttk.Treeview` + `Scrollbar` |

---

## 4. Repair Job Workflow

```
Customer brings device
        ↓
[Staff] Register customer (if new) → Create Job Order → Print receipt
        ↓
[Staff] Assign technician          → Status: Received
        ↓
[Technician] Diagnose              → Status: Diagnosing
        ↓
   Needs parts? ── yes → Status: Waiting for Parts
        ↓ no / parts arrived
[Technician] Repair                → Status: Under Repair
        ↓
[Technician] Mark done             → Status: Completed
        ↓
[Staff] Compute bill → Receive payment → Print official receipt
        ↓
[Staff] Release device             → Status: Released
```

---

## 5. Data Requirements

Each record can be stored as a dictionary and saved as a CSV or JSON file.

| Entity | Fields |
|---|---|
| **User** | user_id, username, password, role, full_name |
| **Customer** | customer_id, name, contact_no, email, address |
| **Job Order** | job_id, customer_id, device_type, brand, model, serial_no, accessories, problem, condition, priority, date_received, est_completion, technician_id, status, diagnosis, notes |
| **Service** | service_id, name, description, price |
| **Job Service** (link) | job_id, service_id |
| **Part** | part_id, name, quantity, unit_price |
| **Job Part** (link) | job_id, part_id, quantity_used |
| **Payment** | payment_id, job_id, amount, method, date |
| **Status Log** | job_id, status, timestamp |

Suggested files: `users.csv`, `customers.csv`, `jobs.csv`, `services.csv`, `parts.csv`, `payments.csv` inside a `data/` folder.

---

## 6. Suggested Screens

1. Login window
2. Main dashboard / menu
3. Customer management (form + table)
4. New job order form
5. Job order list (with status filter and search)
6. Job details / update status (Technician view)
7. Services management
8. Parts inventory
9. Billing & payment window
10. Receipt window
11. Reports window

---

## 7. Mapping to Course Lessons

| Lesson topic | Where it is used in the system |
|---|---|
| Variables, data types, casting | Converting price/quantity inputs (`float()`, `int()`, `str()`) |
| Operators | Computing totals, balance, change |
| `if / elif / else` | Role-based menu, status validation |
| `for` / `while` loops | Displaying records, searching lists |
| `break / continue / pass` | Search loops, skipped records |
| Strings | Formatting receipts, input cleaning (`strip()`, `upper()`, `format`) |
| Lists, tuples | Collections of jobs, fixed status list |
| Dictionaries | Individual customer, job, and service records |
| Functions | `add_customer()`, `compute_total()`, `save_data()` |
| Modules / packages | Splitting code into `gui`, `storage`, `models` |
| Date and time | Date received, status timestamps, daily reports |
| File I/O | Saving/loading all records, exporting receipts |
| `os` module | Create folders, check files, backups |
| Exception handling | File errors, invalid input, empty fields |
| Tkinter widgets | All screens (Entry, Button, Listbox, Frame, Toplevel, etc.) |

---

## 8. Non-Functional Requirements (Brief)

| ID | Requirement |
|---|---|
| NFR-01 | Usability: a new user can create a job order within 2 minutes without help. |
| NFR-02 | Reliability: the program shall not crash on invalid input or missing files. |
| NFR-03 | Performance: lists and searches shall respond within 2 seconds for up to 1,000 records. |
| NFR-04 | Portability: runs on Windows with standard Python 3 installed (no extra packages required). |
| NFR-05 | Maintainability: code shall be split into functions/modules with comments. |

---

## 9. Out of Scope

- Online/web access or multi-computer networking
- Real SMS/email notifications
- Barcode/QR scanning
- Payment gateway integration
- Password encryption (basic storage acceptable for this project)

---

## 10. Suggested Development Priority

1. **Phase 1 (Core):** Login, Customers, Job Orders, Services, Status tracking, File storage
2. **Phase 2:** Billing/payment, Receipts, Search/filter
3. **Phase 3 (if time allows):** Parts inventory, Reports, Backup, Export
