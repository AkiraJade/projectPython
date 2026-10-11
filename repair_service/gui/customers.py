# Customer management screen module

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators


def show_customers_frame(parent, current_user):
    """
    Renders customer list table and management actions inside parent frame.
    """
    # Container frame
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    # Top header bar: Title and Search
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        header_frame,
        text="Customer Management",
        font=("Arial", 14, "bold")
    ).pack(side="left")

    search_frame = ttk.Frame(header_frame)
    search_frame.pack(side="right")

    ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=22)
    search_entry.pack(side="left")

    # Table frame with Treeview and Scrollbars
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    columns = ("customer_id", "name", "contact_no", "email", "address")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("customer_id", text="Customer ID")
    tree.heading("name", text="Full Name")
    tree.heading("contact_no", text="Contact No.")
    tree.heading("email", text="Email")
    tree.heading("address", text="Address")

    tree.column("customer_id", width=100, anchor="center")
    tree.column("name", width=160)
    tree.column("contact_no", width=120)
    tree.column("email", width=180)
    tree.column("address", width=220)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # Functions to refresh and filter table data
    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        customers = storage.load_customers()
        query = query.strip().lower()

        for c in customers:
            cid = c.get("customer_id", "")
            name = c.get("name", "")
            contact = c.get("contact_no", "")
            email = c.get("email", "")
            address = c.get("address", "")

            # Filter logic
            if query:
                if (query not in cid.lower() and
                    query not in name.lower() and
                    query not in contact.lower()):
                    continue

            tree.insert("", "end", values=(cid, name, contact, email, address))

    def on_search_change(event=None):
        refresh_table(search_entry.get())

    search_entry.bind("<KeyRelease>", on_search_change)

    # Dialog for Add / Edit
    def open_customer_dialog(customer_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = customer_to_edit is not None
        title_text = "Edit Customer" if is_edit else "Add New Customer"
        dialog.title(title_text)
        dialog.geometry("400x320")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Full Name:").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(form, width=28)
        name_entry.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Contact No:").grid(row=1, column=0, sticky="w", pady=6)
        contact_entry = ttk.Entry(form, width=28)
        contact_entry.grid(row=1, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Email:").grid(row=2, column=0, sticky="w", pady=6)
        email_entry = ttk.Entry(form, width=28)
        email_entry.grid(row=2, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Address:").grid(row=3, column=0, sticky="w", pady=6)
        address_entry = ttk.Entry(form, width=28)
        address_entry.grid(row=3, column=1, pady=6, padx=(10, 0))

        if is_edit:
            name_entry.insert(0, customer_to_edit.get("name", ""))
            contact_entry.insert(0, customer_to_edit.get("contact_no", ""))
            email_entry.insert(0, customer_to_edit.get("email", ""))
            address_entry.insert(0, customer_to_edit.get("address", ""))

        name_entry.focus()

        def save_customer():
            name = name_entry.get().strip()
            contact = contact_entry.get().strip()
            email = email_entry.get().strip()
            address = address_entry.get().strip()

            # Validations
            if not validators.is_non_empty(name):
                messagebox.showerror("Validation Error", "Full name is required.", parent=dialog)
                return
            if not validators.is_valid_phone(contact):
                messagebox.showerror("Validation Error", "Please enter a valid contact number (at least 7 digits).", parent=dialog)
                return
            if not validators.is_valid_email(email):
                messagebox.showerror("Validation Error", "Please enter a valid email address.", parent=dialog)
                return
            if not validators.is_non_empty(address):
                messagebox.showerror("Validation Error", "Address is required.", parent=dialog)
                return

            customers = storage.load_customers()

            if is_edit:
                cid = customer_to_edit["customer_id"]
                for c in customers:
                    if c.get("customer_id") == cid:
                        c["name"] = name
                        c["contact_no"] = contact
                        c["email"] = email
                        c["address"] = address
                        break
                storage.save_customers(customers)
                messagebox.showinfo("Success", "Customer updated successfully.", parent=dialog)
            else:
                new_id = models.generate_id("CUST-", customers, "customer_id")
                new_customer = {
                    "customer_id": new_id,
                    "name": name,
                    "contact_no": contact,
                    "email": email,
                    "address": address
                }
                customers.append(new_customer)
                storage.save_customers(customers)
                messagebox.showinfo("Success", f"Customer {new_id} added successfully.", parent=dialog)

            dialog.destroy()
            refresh_table(search_entry.get())

        btn_box = ttk.Frame(form)
        btn_box.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        save_btn = ttk.Button(btn_box, text="Save", command=save_customer)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(btn_box, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

    def on_add():
        open_customer_dialog()

    def on_edit():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a customer to edit.")
            return
        cid = tree.item(selected[0], "values")[0]
        customers = storage.load_customers()
        for c in customers:
            if c.get("customer_id") == cid:
                open_customer_dialog(c)
                break

    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a customer to delete.")
            return
        cid = tree.item(selected[0], "values")[0]
        name = tree.item(selected[0], "values")[1]

        # Block deletion if customer has active jobs (FR-09)
        jobs = storage.load_jobs()
        active_jobs = [j for j in jobs if j.get("customer_id") == cid and j.get("status") in models.ACTIVE_STATUSES]
        if active_jobs:
            messagebox.showerror(
                "Deletion Blocked",
                f"Customer {name} ({cid}) has {len(active_jobs)} active job order(s) and cannot be deleted."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete customer {name} ({cid})?"
        )
        if not confirm:
            return

        customers = storage.load_customers()
        updated_customers = [c for c in customers if c.get("customer_id") != cid]
        storage.save_customers(updated_customers)
        messagebox.showinfo("Deleted", f"Customer {name} has been deleted.")
        refresh_table(search_entry.get())

    def on_view_history():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a customer to view repair history.")
            return
        cid = tree.item(selected[0], "values")[0]
        name = tree.item(selected[0], "values")[1]

        jobs = storage.load_jobs()
        cust_jobs = [j for j in jobs if j.get("customer_id") == cid]

        history_win = tk.Toplevel(parent)
        history_win.transient(parent.winfo_toplevel())
        history_win.title(f"Repair History - {name} ({cid})")
        history_win.geometry("620x350")

        hist_frame = ttk.Frame(history_win, padding=15)
        hist_frame.pack(fill="both", expand=True)

        ttk.Label(
            hist_frame,
            text=f"Repair History for {name}",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        if not cust_jobs:
            ttk.Label(hist_frame, text="No repair jobs recorded for this customer.").pack(pady=20)
        else:
            cols = ("job_id", "device", "problem", "status", "date")
            htree = ttk.Treeview(hist_frame, columns=cols, show="headings", height=8)
            htree.heading("job_id", text="Job ID")
            htree.heading("device", text="Device")
            htree.heading("problem", text="Problem")
            htree.heading("status", text="Status")
            htree.heading("date", text="Date Received")

            htree.column("job_id", width=80, anchor="center")
            htree.column("device", width=120)
            htree.column("problem", width=180)
            htree.column("status", width=100, anchor="center")
            htree.column("date", width=100, anchor="center")

            for j in cust_jobs:
                dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
                htree.insert("", "end", values=(
                    j.get("job_id", ""),
                    dev,
                    j.get("problem", ""),
                    j.get("status", ""),
                    j.get("date_received", "")
                ))

            h_scroll = ttk.Scrollbar(hist_frame, orient="vertical", command=htree.yview)
            htree.configure(yscrollcommand=h_scroll.set)
            htree.pack(side="left", fill="both", expand=True)
            h_scroll.pack(side="right", fill="y")

    # Action buttons bar
    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", pady=(10, 0))

    ttk.Button(btn_bar, text="Add Customer", command=on_add).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="Edit Customer", command=on_edit).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="Delete Customer", command=on_delete).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="View History", command=on_view_history).pack(side="left", padx=5)

    # Initial load
    refresh_table()

    return frame
