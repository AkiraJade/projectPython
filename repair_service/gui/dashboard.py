# Dashboard and main menu navigation module with modern slate sidebar and active tab highlights

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
import gui.theme as theme


def show_dashboard_window(root, current_user, on_logout):
    """
    Renders main dashboard with modern slate sidebar, top header bar,
    and active menu highlights (FR-73).
    """
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Computer & Laptop Repair Service System")
    theme.center_window(root, 1100, 700, 960, 600)
    root.resizable(True, True)

    role = current_user.get("role", "Customer")
    full_name = current_user.get("full_name", current_user.get("username", "User"))

    # Main layout container
    main_layout = ttk.Frame(root)
    main_layout.pack(fill="both", expand=True)

    # 1. Left Sidebar Navigation
    sidebar = ttk.Frame(main_layout, style="Sidebar.TFrame", padding=(12, 16))
    sidebar.pack(side="left", fill="y", expand=False)
    sidebar.configure(width=220)
    sidebar.pack_propagate(False)

    # Brand Title
    ttk.Label(
        sidebar,
        text="TechRepair",
        style="Brand.TLabel"
    ).pack(anchor="w", padx=6, pady=(4, 2))

    ttk.Label(
        sidebar,
        text="Service Dashboard",
        background=theme.BG_SIDEBAR,
        foreground="#94A3B8",
        font=theme.FONT_MUTED
    ).pack(anchor="w", padx=6, pady=(0, 16))

    ttk.Separator(sidebar).pack(fill="x", padx=6, pady=(0, 12))

    ttk.Label(
        sidebar,
        text="NAVIGATION",
        style="SidebarHeader.TLabel"
    ).pack(anchor="w", padx=8, pady=(0, 8))

    # 2. Right Body Container (Top Header + Content Area)
    right_container = ttk.Frame(main_layout)
    right_container.pack(side="right", fill="both", expand=True)

    # Top Header Bar (White Surface)
    top_header = ttk.Frame(right_container, style="Surface.TFrame", padding=(20, 14))
    top_header.pack(side="top", fill="x")

    page_title_label = ttk.Label(
        top_header,
        text="Dashboard",
        style="Surface.TLabel",
        font=theme.FONT_SECTION
    )
    page_title_label.pack(side="left")

    user_info_label = ttk.Label(
        top_header,
        text=f"{full_name}  •  {role}",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY_BOLD
    )
    user_info_label.pack(side="right")

    # Thin border below header
    ttk.Separator(right_container, orient="horizontal").pack(fill="x")

    # Content Area
    content_area = ttk.Frame(right_container, padding=16)
    content_area.pack(side="bottom", fill="both", expand=True)

    current_screen_holder = {"frame": None}
    menu_buttons = {}
    active_key_holder = {"key": None}

    def clear_content_area():
        if current_screen_holder["frame"] is not None:
            current_screen_holder["frame"].destroy()
            current_screen_holder["frame"] = None

    def set_active_screen(key, title, render_fn):
        """Highlights the active sidebar button, updates title, and swaps view."""
        clear_content_area()
        page_title_label.configure(text=title)

        # Update button styles
        for k, btn in menu_buttons.items():
            if k == key:
                btn.configure(style="SidebarActive.TButton")
            else:
                btn.configure(style="Sidebar.TButton")
        active_key_holder["key"] = key

        # Render screen inside content_area
        current_screen_holder["frame"] = render_fn()

    # Customer Screen Wrappers
    def show_new_request():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can submit new online requests.")
            return
        set_active_screen(
            "new_request",
            "Submit New Repair Request",
            lambda: customer_portal_gui.show_new_request_frame(
                content_area,
                current_user,
                on_success_callback=show_my_requests
            )
        )

    def show_my_requests():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can view this portal.")
            return
        set_active_screen(
            "my_requests",
            "My Repair Requests",
            lambda: customer_portal_gui.show_my_requests_frame(content_area, current_user)
        )

    def show_my_receipts():
        if role != "Customer":
            messagebox.showerror("Access Denied", "Only customers can view this portal.")
            return
        set_active_screen(
            "my_receipts",
            "My Receipts & Invoices",
            lambda: customer_portal_gui.show_my_receipts_frame(content_area, current_user)
        )

    def show_profile():
        set_active_screen(
            "profile",
            "Profile & Account Settings",
            lambda: customer_portal_gui.show_profile_frame(content_area, current_user)
        )

    # Staff / Admin Screen Wrappers
    def show_incoming():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "Access restricted to Staff and Admin.")
            return
        set_active_screen(
            "incoming",
            "Incoming Online Requests",
            lambda: incoming_requests_gui.show_incoming_requests_frame(content_area, current_user)
        )

    def show_jobs():
        if role not in ["Admin", "Staff", "Technician"]:
            messagebox.showerror("Access Denied", "Access restricted.")
            return
        title = "My Assigned Jobs" if role == "Technician" else "Job Orders & Repair Tracking"
        set_active_screen(
            "jobs",
            title,
            lambda: jobs_gui.show_jobs_frame(content_area, current_user)
        )

    def show_customers():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "Access restricted to Staff and Admin.")
            return
        set_active_screen(
            "customers",
            "Customer Management",
            lambda: customers_gui.show_customers_frame(content_area, current_user)
        )

    def show_billing():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "Access restricted to Staff and Admin.")
            return
        set_active_screen(
            "billing",
            "Billing & Payment Management",
            lambda: billing_gui.show_billing_frame(content_area, current_user)
        )

    def show_parts():
        if role not in ["Admin", "Staff", "Technician"]:
            messagebox.showerror("Access Denied", "Access restricted.")
            return
        set_active_screen(
            "parts",
            "Parts & Inventory Management",
            lambda: parts_gui.show_parts_frame(content_area, current_user)
        )

    def show_services():
        if role != "Admin":
            messagebox.showerror("Access Denied", "Access restricted to Administrator.")
            return
        set_active_screen(
            "services",
            "Service Catalog Management",
            lambda: services_gui.show_services_frame(content_area, current_user)
        )

    def show_reports():
        if role not in ["Admin", "Staff"]:
            messagebox.showerror("Access Denied", "Access restricted to Staff and Admin.")
            return
        set_active_screen(
            "reports",
            "Reports & System Analytics",
            lambda: reports_gui.show_reports_frame(content_area, current_user)
        )

    def show_users():
        if role != "Admin":
            messagebox.showerror("Access Denied", "Access restricted to Administrator.")
            return
        set_active_screen(
            "users",
            "User Accounts Management",
            lambda: users_gui.show_users_frame(content_area, current_user)
        )

    def perform_logout():
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out?")
        if confirm:
            on_logout()

    # Create Sidebar Buttons by Role
    def add_menu_btn(key, text, command):
        btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=command)
        btn.pack(fill="x", pady=2)
        menu_buttons[key] = btn
        return btn

    if role == "Customer":
        add_menu_btn("new_request", "New Request", show_new_request)
        add_menu_btn("my_requests", "My Requests", show_my_requests)
        add_menu_btn("my_receipts", "My Receipts", show_my_receipts)
        add_menu_btn("profile", "Profile", show_profile)

    elif role in ["Admin", "Staff"]:
        add_menu_btn("incoming", "Incoming Requests", show_incoming)
        add_menu_btn("jobs", "Job Orders", show_jobs)
        add_menu_btn("customers", "Customers", show_customers)
        add_menu_btn("billing", "Billing & Payments", show_billing)
        add_menu_btn("parts", "Parts Inventory", show_parts)

        if role == "Admin":
            add_menu_btn("services", "Service Catalog", show_services)
            add_menu_btn("reports", "Reports & Analytics", show_reports)
            add_menu_btn("users", "User Accounts", show_users)
        else:
            add_menu_btn("reports", "Reports & Analytics", show_reports)

    elif role == "Technician":
        add_menu_btn("jobs", "My Assigned Jobs", show_jobs)
        add_menu_btn("parts", "Parts Inventory", show_parts)

    # Spacer pushing Log Out to bottom
    ttk.Frame(sidebar, style="Sidebar.TFrame").pack(fill="both", expand=True)

    # Bottom Logout Button
    ttk.Separator(sidebar).pack(fill="x", padx=6, pady=(0, 8))
    btn_logout = ttk.Button(sidebar, text="Sign Out", style="Sidebar.TButton", command=perform_logout)
    btn_logout.pack(fill="x", side="bottom", pady=(0, 4))

    # Initial Screen Launch
    if role == "Customer":
        show_my_requests()
    elif role in ["Admin", "Staff"]:
        show_incoming()
    else:
        show_jobs()
