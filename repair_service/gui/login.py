# Login screen module with Customer registration

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators


def show_login_window(root, on_login_success):
    """
    Renders the login screen inside root window.
    When login succeeds, calls on_login_success(logged_in_user).
    """
    # Clear any previous widgets in root
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Computer & Laptop Repair Service - Login")
    root.geometry("420x350")
    root.resizable(False, False)

    # Center container frame
    container = ttk.Frame(root, padding=25)
    container.pack(expand=True, fill="both")

    # Header title
    title_label = ttk.Label(
        container,
        text="Repair Service System",
        font=("Arial", 16, "bold")
    )
    title_label.pack(pady=(0, 5))

    subtitle_label = ttk.Label(
        container,
        text="Please log in with your credentials",
        font=("Arial", 9)
    )
    subtitle_label.pack(pady=(0, 15))

    # Form fields frame
    form_frame = ttk.Frame(container)
    form_frame.pack(fill="x")

    ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=6)
    username_entry = ttk.Entry(form_frame, width=28)
    username_entry.grid(row=0, column=1, pady=6, padx=(10, 0))
    username_entry.focus()

    ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=6)
    password_entry = ttk.Entry(form_frame, width=28, show="*")
    password_entry.grid(row=1, column=1, pady=6, padx=(10, 0))

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
        dialog.geometry("420x380")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Create Customer Account", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

        ttk.Label(form, text="Full Name:").grid(row=1, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(form, width=26)
        name_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(form, text="Contact No:").grid(row=2, column=0, sticky="w", pady=5)
        contact_entry = ttk.Entry(form, width=26)
        contact_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(form, text="Email:").grid(row=3, column=0, sticky="w", pady=5)
        email_entry = ttk.Entry(form, width=26)
        email_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(form, text="Address:").grid(row=4, column=0, sticky="w", pady=5)
        address_entry = ttk.Entry(form, width=26)
        address_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        ttk.Label(form, text="Username:").grid(row=5, column=0, sticky="w", pady=5)
        reg_uname_entry = ttk.Entry(form, width=26)
        reg_uname_entry.grid(row=5, column=1, pady=5, padx=(10, 0))

        ttk.Label(form, text="Password:").grid(row=6, column=0, sticky="w", pady=5)
        reg_pwd_entry = ttk.Entry(form, width=26, show="*")
        reg_pwd_entry.grid(row=6, column=1, pady=5, padx=(10, 0))

        name_entry.focus()

        def submit_registration():
            full_name = name_entry.get().strip()
            contact_no = contact_entry.get().strip()
            email = email_entry.get().strip()
            address = address_entry.get().strip()
            username = reg_uname_entry.get().strip()
            password = reg_pwd_entry.get().strip()

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
                    messagebox.showerror("Username Taken", f"Username '{username}' is already in use. Please choose another.", parent=dialog)
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
                f"Customer account created successfully!\nCustomer ID: {new_cust_id}\nUsername: {username}\nYou can now log in.",
                parent=dialog
            )
            dialog.destroy()

            # Pre-fill login username
            username_entry.delete(0, tk.END)
            username_entry.insert(0, username)
            password_entry.delete(0, tk.END)
            password_entry.focus()

        btn_box = ttk.Frame(form)
        btn_box.grid(row=7, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_box, text="Register", command=submit_registration).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    # Bind Enter key to submit
    password_entry.bind("<Return>", attempt_login)
    username_entry.bind("<Return>", attempt_login)

    # Action buttons
    button_frame = ttk.Frame(container)
    button_frame.pack(fill="x", pady=(15, 0))

    login_button = ttk.Button(button_frame, text="Log In", command=attempt_login)
    login_button.pack(fill="x", pady=(0, 6))

    register_button = ttk.Button(button_frame, text="Register as Customer", command=open_register_dialog)
    register_button.pack(fill="x")
