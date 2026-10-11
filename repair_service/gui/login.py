# Login screen module with modern split-panel layout and clean registration dialog

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators
import gui.theme as theme


def show_login_window(root, on_login_success):
    """
    Renders modern split-panel login screen inside root window.
    When login succeeds, calls on_login_success(logged_in_user).
    """
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Computer & Laptop Repair Service System - Login")
    theme.center_window(root, 680, 400, 600, 360)
    root.resizable(False, False)

    # Main container
    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    # 1. Left Brand Panel (Slate Sidebar Theme)
    brand_panel = ttk.Frame(container, style="Sidebar.TFrame", padding=30)
    brand_panel.pack(side="left", fill="both", expand=False)
    brand_panel.configure(width=260)
    brand_panel.pack_propagate(False)

    ttk.Label(
        brand_panel,
        text="TechRepair",
        style="Brand.TLabel",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(20, 6))

    ttk.Label(
        brand_panel,
        text="Computer & Laptop\nRepair Service System",
        background=theme.BG_SIDEBAR,
        foreground="#CBD5E1",
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(0, 20))

    ttk.Separator(brand_panel).pack(fill="x", pady=(0, 20))

    info_text = (
        "Streamlined repair tracking,\n"
        "device intake management,\n"
        "and client invoicing."
    )
    ttk.Label(
        brand_panel,
        text=info_text,
        background=theme.BG_SIDEBAR,
        foreground="#94A3B8",
        font=theme.FONT_MUTED
    ).pack(anchor="w")

    # 2. Right Form Panel (White Surface)
    form_panel = ttk.Frame(container, style="Surface.TFrame", padding=(35, 30))
    form_panel.pack(side="right", fill="both", expand=True)

    ttk.Label(
        form_panel,
        text="Sign In",
        style="Surface.TLabel",
        font=theme.FONT_TITLE
    ).pack(anchor="w")

    ttk.Label(
        form_panel,
        text="Enter your credentials to access your dashboard",
        style="SurfaceMuted.TLabel"
    ).pack(anchor="w", pady=(2, 20))

    # Form inputs
    inputs_frame = ttk.Frame(form_panel, style="Surface.TFrame")
    inputs_frame.pack(fill="x")

    ttk.Label(inputs_frame, text="Username", style="Surface.TLabel", font=theme.FONT_BODY_BOLD).pack(anchor="w", pady=(0, 4))
    username_entry = ttk.Entry(inputs_frame, width=32)
    username_entry.pack(fill="x", pady=(0, 14))
    username_entry.focus()

    ttk.Label(inputs_frame, text="Password", style="Surface.TLabel", font=theme.FONT_BODY_BOLD).pack(anchor="w", pady=(0, 4))
    password_entry = ttk.Entry(inputs_frame, width=32, show="*")
    password_entry.pack(fill="x", pady=(0, 20))

    def attempt_login(event=None):
        uname = username_entry.get().strip()
        pwd = password_entry.get().strip()

        if not uname or not pwd:
            messagebox.showwarning("Incomplete Form", "Please enter both username and password.")
            return

        users = storage.load_users()
        found_user = None
        for user in users:
            if user.get("username") == uname and user.get("password") == pwd:
                found_user = user
                break

        if found_user:
            on_login_success(found_user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            password_entry.delete(0, tk.END)

    def open_register_dialog():
        dialog = tk.Toplevel(root)
        dialog.transient(root)
        dialog.grab_set()
        dialog.title("Customer Registration")
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 460, 460, 420, 420)
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, style="Surface.TFrame", padding=25)
        form.pack(fill="both", expand=True)

        ttk.Label(
            form,
            text="Create Customer Account",
            style="Surface.TLabel",
            font=theme.FONT_SECTION
        ).pack(anchor="w")

        ttk.Label(
            form,
            text="Register to track repairs and submit service requests online",
            style="SurfaceMuted.TLabel"
        ).pack(anchor="w", pady=(2, 16))

        grid_frame = ttk.Frame(form, style="Surface.TFrame")
        grid_frame.pack(fill="x")

        fields = [
            ("Full Name:", 0),
            ("Contact Number:", 1),
            ("Email Address:", 2),
            ("Home / Office Address:", 3),
            ("Username:", 4),
            ("Password:", 5),
        ]

        entries = {}
        for label_text, row_idx in fields:
            ttk.Label(
                grid_frame,
                text=label_text,
                style="Surface.TLabel",
                font=theme.FONT_BODY
            ).grid(row=row_idx, column=0, sticky="w", pady=5)

            is_pwd = label_text.startswith("Password")
            ent = ttk.Entry(grid_frame, width=28, show="*" if is_pwd else "")
            ent.grid(row=row_idx, column=1, sticky="e", pady=5, padx=(12, 0))
            entries[label_text] = ent

        entries["Full Name:"].focus()

        def submit_registration():
            full_name = entries["Full Name:"].get().strip()
            contact_no = entries["Contact Number:"].get().strip()
            email = entries["Email Address:"].get().strip()
            address = entries["Home / Office Address:"].get().strip()
            username = entries["Username:"].get().strip()
            password = entries["Password:"].get().strip()

            if not validators.is_non_empty(full_name):
                messagebox.showerror("Validation Error", "Full Name is required.", parent=dialog)
                return
            if not validators.is_valid_phone(contact_no):
                messagebox.showerror("Validation Error", "Please enter a valid contact number (at least 7 digits).", parent=dialog)
                return
            if not validators.is_valid_email(email):
                messagebox.showerror("Validation Error", "Please enter a valid email address.", parent=dialog)
                return
            if not validators.is_non_empty(address):
                messagebox.showerror("Validation Error", "Address is required.", parent=dialog)
                return
            if not validators.is_non_empty(username):
                messagebox.showerror("Validation Error", "Username is required.", parent=dialog)
                return
            if not validators.is_non_empty(password):
                messagebox.showerror("Validation Error", "Password is required.", parent=dialog)
                return

            users = storage.load_users()
            for u in users:
                if u.get("username", "").lower() == username.lower():
                    messagebox.showerror("Username Taken", f"Username '{username}' is already taken.", parent=dialog)
                    return

            customers = storage.load_customers()
            new_cust_id = models.generate_id("CUST-", customers, "customer_id")
            new_customer = {
                "customer_id": new_cust_id,
                "name": full_name,
                "contact_no": contact_no,
                "email": email,
                "address": address
            }
            customers.append(new_customer)
            storage.save_customers(customers)

            new_user_id = models.generate_id("USR-", users, "user_id")
            new_user = {
                "user_id": new_user_id,
                "username": username,
                "password": password,
                "role": "Customer",
                "full_name": full_name,
                "customer_id": new_cust_id
            }
            users.append(new_user)
            storage.save_users(users)

            messagebox.showinfo(
                "Registration Successful",
                f"Customer account created successfully!\n\nCustomer ID: {new_cust_id}\nUsername: {username}\n\nYou may now sign in.",
                parent=dialog
            )
            dialog.destroy()

            username_entry.delete(0, tk.END)
            username_entry.insert(0, username)
            password_entry.delete(0, tk.END)
            password_entry.focus()

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(24, 0))

        ttk.Button(
            btn_row,
            text="Cancel",
            style="Secondary.TButton",
            command=dialog.destroy
        ).pack(side="left")

        ttk.Button(
            btn_row,
            text="Create Account",
            style="Primary.TButton",
            command=submit_registration
        ).pack(side="right")

    # Enter key binding
    password_entry.bind("<Return>", attempt_login)
    username_entry.bind("<Return>", attempt_login)

    # Buttons
    login_btn = ttk.Button(form_panel, text="Sign In", style="Primary.TButton", command=attempt_login)
    login_btn.pack(fill="x", pady=(0, 10))

    register_btn = ttk.Button(form_panel, text="Create a Customer Account", style="Secondary.TButton", command=open_register_dialog)
    register_btn.pack(fill="x")
