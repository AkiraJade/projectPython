# Dashboard and main menu navigation module with strict role checks

import tkinter as tk
from tkinter import ttk, messagebox
import gui.customers as customers_gui
import gui.jobs as jobs_gui
import gui.services as services_gui
import gui.billing as billing_gui
import gui.parts as parts_gui
import gui.reports as reports_gui
import gui.users as users_gui
import gui.customer_portal as customer_portal_gui
import gui.incoming_requests as incoming_requests_gui


def show_dashboard_window(root, current_user, on_logout):
    """
    Renders main dashboard with role-based navigation and content area.
    Strictly isolates Customer, Technician, Staff, and Admin views (FR-73).
    """
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Computer & Laptop Repair Service System")
    root.geometry("1020x660")
    root.minsize(860, 540)
    root.resizable(True, True)

    role = current_user.get("role", "Customer")
    full_name = current_user.get("full_name", current_user.get("username", "User"))

    # Top App Bar
    app_bar = ttk.Frame(root, padding=(15, 10))
    app_bar.pack(fill="x", side="top")

    system_title = ttk.Label(
        app_bar,
        text="Repair Service System",
        font=("Arial", 14, "bold")
    )
    system_title.pack(side="left")

    user_info = ttk.Label(
        app_bar,
        text=f"Logged in as: {full_name} ({role})",
        font=("Arial", 10)
    )
    user_info.pack(side="right")

    # Separator
    ttk.Separator(root, orient="horizontal").pack(fill="x")

    # Main layout: Left sidebar for navigation, Right frame for screen content
    main_body = ttk.Frame(root)
    main_body.pack(fill="both", expand=True)

    sidebar = ttk.Frame(main_body, width=190, padding=10)
    sidebar.pack(side="left", fill="y")

    ttk.Separator(main_body, orient="vertical").pack(side="left", fill="y")

    content_area = ttk.Frame(main_body, padding=10)
    content_area.pack(side="right", fill="both", expand=True)

    current_screen_holder = {"frame": None}

    def clear_content_area():
        if current_screen_holder["frame"] is not None:
            current_screen_holder["frame"].destroy()
            current_screen_holder["frame"] = None

    # Customer screens
    def switch_to_new_request():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can submit new online requests.")
            return
        clear_content_area()
        current_screen_holder["frame"] = customer_portal_gui.show_new_request_frame(
            content_area,
            current_user,
            on_success_callback=switch_to_my_requests
        )

    def switch_to_my_requests():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can view the customer request portal.")
            return
        clear_content_area()
        current_screen_holder["frame"] = customer_portal_gui.show_my_requests_frame(content_area, current_user)

    def switch_to_my_receipts():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can view this receipts portal.")
            return
        clear_content_area()
        current_screen_holder["frame"] = customer_portal_gui.show_my_receipts_frame(content_area, current_user)

    def switch_to_profile():
        clear_content_area()
        current_screen_holder["frame"] = customer_portal_gui.show_profile_frame(content_area, current_user)

    # Staff / Admin screens
    def switch_to_incoming_requests():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "You do not have permission to view incoming requests.")
            return
        clear_content_area()
        current_screen_holder["frame"] = incoming_requests_gui.show_incoming_requests_frame(content_area, current_user)

    def switch_to_jobs():
        if role not in ["Admin", "Staff", "Technician"]:
            messagebox.showerror("Access Denied", "You do not have permission to view this section.")
            return
        clear_content_area()
        current_screen_holder["frame"] = jobs_gui.show_jobs_frame(content_area, current_user)

    def switch_to_customers():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "You do not have permission to view customer records.")
            return
        clear_content_area()
        current_screen_holder["frame"] = customers_gui.show_customers_frame(content_area, current_user)

    def switch_to_services():
        if role != "Admin":
            messagebox.showerror("Access Denied", "Only administrators can manage the service catalog.")
            return
        clear_content_area()
        current_screen_holder["frame"] = services_gui.show_services_frame(content_area, current_user)

    def switch_to_billing():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "You do not have permission to access billing.")
            return
        clear_content_area()
        current_screen_holder["frame"] = billing_gui.show_billing_frame(content_area, current_user)

    def switch_to_parts():
        if role not in ["Admin", "Staff", "Technician"]:
            messagebox.showerror("Access Denied", "You do not have permission to view parts inventory.")
            return
        clear_content_area()
        current_screen_holder["frame"] = parts_gui.show_parts_frame(content_area, current_user)

    def switch_to_reports():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "You do not have permission to view system reports.")
            return
        clear_content_area()
        current_screen_holder["frame"] = reports_gui.show_reports_frame(content_area, current_user)

    def switch_to_users():
        if role != "Admin":
            messagebox.showerror("Access Denied", "Only administrators can manage user accounts.")
            return
        clear_content_area()
        current_screen_holder["frame"] = users_gui.show_users_frame(content_area, current_user)

    def perform_logout():
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            on_logout()

    # Sidebar Navigation Buttons based strictly on Role
    ttk.Label(sidebar, text="MAIN MENU", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 10))

    if role == "Customer":
        ttk.Button(sidebar, text="New Request", command=switch_to_new_request).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="My Requests", command=switch_to_my_requests).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="My Receipts", command=switch_to_my_receipts).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Profile", command=switch_to_profile).pack(fill="x", pady=3)

    elif role in ["Admin", "Staff"]:
        ttk.Button(sidebar, text="Incoming Requests", command=switch_to_incoming_requests).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Job Orders", command=switch_to_jobs).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Customers", command=switch_to_customers).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Billing & Payments", command=switch_to_billing).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Parts & Inventory", command=switch_to_parts).pack(fill="x", pady=3)

        if role == "Admin":
            ttk.Button(sidebar, text="Service Catalog", command=switch_to_services).pack(fill="x", pady=3)
            ttk.Button(sidebar, text="Reports & Analytics", command=switch_to_reports).pack(fill="x", pady=3)
            ttk.Button(sidebar, text="User Accounts", command=switch_to_users).pack(fill="x", pady=3)
        else:
            ttk.Button(sidebar, text="Reports & Analytics", command=switch_to_reports).pack(fill="x", pady=3)

    elif role == "Technician":
        ttk.Button(sidebar, text="My Jobs", command=switch_to_jobs).pack(fill="x", pady=3)
        ttk.Button(sidebar, text="Parts Inventory", command=switch_to_parts).pack(fill="x", pady=3)

    # Spacer
    ttk.Frame(sidebar).pack(fill="both", expand=True)

    # Logout button at bottom of sidebar
    ttk.Button(sidebar, text="Log Out", command=perform_logout).pack(fill="x", side="bottom", pady=5)

    # Default initial screen view based on role
    if role == "Customer":
        switch_to_my_requests()
    elif role in ["Admin", "Staff"]:
        switch_to_incoming_requests()
    else:
        switch_to_jobs()
