# Customer management screen module with modern table styling and centered forms

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators
import gui.theme as theme


def show_customers_frame(parent, current_user):
    """
    Renders customer list table and management actions inside a modern card.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    card.pack(fill="both", expand=True)

    # Top Toolbar: Action Buttons on Left, Search on Right
    toolbar = ttk.Frame(card, style="Surface.TFrame")
    toolbar.pack(fill="x", pady=(0, 12))

    btn_bar = ttk.Frame(toolbar, style="Surface.TFrame")
    btn_bar.pack(side="left")

    search_frame = ttk.Frame(toolbar, style="Surface.TFrame")
    search_frame.pack(side="right")

    ttk.Label(search_frame, text="Search:", style="Surface.TLabel", font=theme.FONT_BODY).pack(side="left", padx=(0, 6))
    search_entry = ttk.Entry(search_frame, width=22)
    search_entry.pack(side="left")

    # Table Container
    table_frame = ttk.Frame(card, style="Surface.TFrame")
    table_frame.pack(fill="both", expand=True)

    columns = ("customer_id", "name", "contact_no", "email", "address")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("customer_id", text="Customer ID")
    tree.heading("name", text="Full Name")
    tree.heading("contact_no", text="Contact No.")
    tree.heading("email", text="Email Address")
    tree.heading("address", text="Address")

    tree.column("customer_id", width=110, anchor="center")
    tree.column("name", width=180)
    tree.column("contact_no", width=130)
    tree.column("email", width=200)
    tree.column("address", width=250)

    theme.setup_treeview_tags(tree)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # Empty State Banner
    empty_label = ttk.Label(
        card,
        text="No customer records found.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        customers = storage.load_customers()
        query = query.strip().lower()
        displayed_count = 0

        for idx, c in enumerate(customers):
            cid = c.get("customer_id", "")
            name = c.get("name", "")
            contact = c.get("contact_no", "")
            email = c.get("email", "")
            address = c.get("address", "")

            if query:
                if (query not in cid.lower() and
                    query not in name.lower() and
                    query not in contact.lower()):
                    continue

            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(cid, name, contact, email, address), tags=(tag,))
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    search_entry.bind("<KeyRelease>", lambda e: refresh_table(search_entry.get()))

    # Dialog for Add / Edit Customer
    def open_customer_dialog(customer_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = customer_to_edit is not None
        title_text = "Edit Customer" if is_edit else "Add New Customer"
        dialog.title(title_text)
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 460, 360, 420, 320)
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, style="Surface.TFrame", padding=24)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=title_text, style="Surface.TLabel", font=theme.FONT_SECTION).pack(anchor="w")
        ttk.Label(form, text="Fields marked with * are required.", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 14))

        grid = ttk.Frame(form, style="Surface.TFrame")
        grid.pack(fill="x")

        ttk.Label(grid, text="Full Name *:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(grid, width=28)
        name_entry.grid(row=0, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Contact No *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        contact_entry = ttk.Entry(grid, width=28)
        contact_entry.grid(row=1, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Email Address *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        email_entry = ttk.Entry(grid, width=28)
        email_entry.grid(row=2, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Address *:", style="Surface.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        address_entry = ttk.Entry(grid, width=28)
        address_entry.grid(row=3, column=1, sticky="e", pady=6, padx=(10, 0))

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

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Save Customer", style="Primary.TButton", command=save_customer).pack(side="right")

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
        updated = [c for c in customers if c.get("customer_id") != cid]
        storage.save_customers(updated)
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
        history_win.configure(bg=theme.BG_SURFACE)
        theme.center_window(history_win, 680, 400, 600, 340)

        hist_frame = ttk.Frame(history_win, style="Surface.TFrame", padding=20)
        hist_frame.pack(fill="both", expand=True)

        ttk.Label(
            hist_frame,
            text=f"Repair History for {name} ({cid})",
            style="Surface.TLabel",
            font=theme.FONT_SECTION
        ).pack(anchor="w", pady=(0, 10))

        if not cust_jobs:
            ttk.Label(hist_frame, text="No repair jobs recorded for this customer.", style="SurfaceMuted.TLabel").pack(pady=40)
        else:
            cols = ("job_id", "device", "problem", "status", "date")
            htree = ttk.Treeview(hist_frame, columns=cols, show="headings", height=8)
            htree.heading("job_id", text="Job ID")
            htree.heading("device", text="Device")
            htree.heading("problem", text="Problem Description")
            htree.heading("status", text="Status")
            htree.heading("date", text="Date Received")

            htree.column("job_id", width=90, anchor="center")
            htree.column("device", width=140)
            htree.column("problem", width=220)
            htree.column("status", width=110, anchor="center")
            htree.column("date", width=120, anchor="center")

            theme.setup_treeview_tags(htree)

            for idx, j in enumerate(cust_jobs):
                dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
                stat = j.get("status", "")
                zebra_tag = "even" if idx % 2 == 0 else "odd"
                status_tag = f"status_{stat}"
                htree.insert("", "end", values=(
                    j.get("job_id", ""),
                    dev,
                    j.get("problem", ""),
                    stat,
                    j.get("date_received", "")
                ), tags=(zebra_tag, status_tag))

            h_scroll = ttk.Scrollbar(hist_frame, orient="vertical", command=htree.yview)
            htree.configure(yscrollcommand=h_scroll.set)
            htree.pack(side="left", fill="both", expand=True)
            h_scroll.pack(side="right", fill="y")

    # Action buttons on Toolbar
    ttk.Button(btn_bar, text="Add Customer", style="Primary.TButton", command=on_add).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Edit Customer", style="Secondary.TButton", command=on_edit).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Delete Customer", style="Secondary.TButton", command=on_delete).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="View History", style="Secondary.TButton", command=on_view_history).pack(side="left")

    refresh_table()
    return card
