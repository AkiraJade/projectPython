# Service catalog management screen module

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators


def show_services_frame(parent, current_user):
    """
    Renders service catalog list and actions inside parent frame.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        header_frame,
        text="Service Catalog",
        font=("Arial", 14, "bold")
    ).pack(side="left")

    search_frame = ttk.Frame(header_frame)
    search_frame.pack(side="right")

    ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=22)
    search_entry.pack(side="left")

    # Table with Treeview
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    columns = ("service_id", "name", "description", "price")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("service_id", text="Service ID")
    tree.heading("name", text="Service Name")
    tree.heading("description", text="Description")
    tree.heading("price", text="Price (PHP)")

    tree.column("service_id", width=100, anchor="center")
    tree.column("name", width=180)
    tree.column("description", width=280)
    tree.column("price", width=110, anchor="e")

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        services = storage.load_services()
        query = query.strip().lower()

        for s in services:
            sid = s.get("service_id", "")
            name = s.get("name", "")
            desc = s.get("description", "")
            price = float(s.get("price", 0.0))

            if query:
                if query not in sid.lower() and query not in name.lower() and query not in desc.lower():
                    continue

            tree.insert("", "end", values=(sid, name, desc, f"{price:,.2f}"))

    def on_search_change(event=None):
        refresh_table(search_entry.get())

    search_entry.bind("<KeyRelease>", on_search_change)

    # Add / Edit dialog
    def open_service_dialog(service_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = service_to_edit is not None
        title_text = "Edit Service" if is_edit else "Add New Service"
        dialog.title(title_text)
        dialog.geometry("400x260")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Service Name:").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(form, width=28)
        name_entry.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Description:").grid(row=1, column=0, sticky="w", pady=6)
        desc_entry = ttk.Entry(form, width=28)
        desc_entry.grid(row=1, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Price (PHP):").grid(row=2, column=0, sticky="w", pady=6)
        price_entry = ttk.Entry(form, width=28)
        price_entry.grid(row=2, column=1, pady=6, padx=(10, 0))

        if is_edit:
            name_entry.insert(0, service_to_edit.get("name", ""))
            desc_entry.insert(0, service_to_edit.get("description", ""))
            price_entry.insert(0, str(service_to_edit.get("price", 0.0)))

        name_entry.focus()

        def save_service():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            price_str = price_entry.get().strip()

            if not validators.is_non_empty(name):
                messagebox.showerror("Validation Error", "Service name is required.", parent=dialog)
                return
            if not validators.is_valid_price(price_str):
                messagebox.showerror("Validation Error", "Please enter a valid price (non-negative number).", parent=dialog)
                return

            price = float(price_str)
            services = storage.load_services()

            if is_edit:
                sid = service_to_edit["service_id"]
                for s in services:
                    if s.get("service_id") == sid:
                        s["name"] = name
                        s["description"] = desc
                        s["price"] = price
                        break
                storage.save_services(services)
                messagebox.showinfo("Success", "Service updated successfully.", parent=dialog)
            else:
                new_id = models.generate_id("SRV-", services, "service_id")
                new_service = {
                    "service_id": new_id,
                    "name": name,
                    "description": desc,
                    "price": price
                }
                services.append(new_service)
                storage.save_services(services)
                messagebox.showinfo("Success", f"Service {new_id} added successfully.", parent=dialog)

            dialog.destroy()
            refresh_table(search_entry.get())

        btn_box = ttk.Frame(form)
        btn_box.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_box, text="Save", command=save_service).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def on_add():
        open_service_dialog()

    def on_edit():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a service to edit.")
            return
        sid = tree.item(selected[0], "values")[0]
        services = storage.load_services()
        for s in services:
            if s.get("service_id") == sid:
                open_service_dialog(s)
                break

    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a service to delete.")
            return
        sid = tree.item(selected[0], "values")[0]
        name = tree.item(selected[0], "values")[1]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete service '{name}' ({sid})?")
        if not confirm:
            return

        services = storage.load_services()
        updated = [s for s in services if s.get("service_id") != sid]
        storage.save_services(updated)
        messagebox.showinfo("Deleted", f"Service '{name}' has been deleted.")
        refresh_table(search_entry.get())

    # Buttons (Admin has CRUD, Staff can view)
    user_role = current_user.get("role", "")
    if user_role == "Admin":
        btn_bar = ttk.Frame(frame)
        btn_bar.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_bar, text="Add Service", command=on_add).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="Edit Service", command=on_edit).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="Delete Service", command=on_delete).pack(side="left", padx=5)

    refresh_table()
    return frame
