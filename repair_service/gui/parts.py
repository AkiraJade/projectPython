# Parts inventory management module

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators

LOW_STOCK_THRESHOLD = 3


def show_parts_frame(parent, current_user):
    """
    Renders parts inventory table, search, low-stock warnings, and add/edit dialogs.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        header_frame,
        text="Parts & Inventory Management",
        font=("Arial", 14, "bold")
    ).pack(side="left")

    search_frame = ttk.Frame(header_frame)
    search_frame.pack(side="right")

    ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
    search_entry = ttk.Entry(search_frame, width=20)
    search_entry.pack(side="left")

    # Table with Treeview
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    columns = ("part_id", "name", "quantity", "unit_price", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("part_id", text="Part ID")
    tree.heading("name", text="Part Name")
    tree.heading("quantity", text="In Stock")
    tree.heading("unit_price", text="Unit Price (PHP)")
    tree.heading("status", text="Stock Status")

    tree.column("part_id", width=90, anchor="center")
    tree.column("name", width=260)
    tree.column("quantity", width=90, anchor="center")
    tree.column("unit_price", width=120, anchor="e")
    tree.column("status", width=120, anchor="center")

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        parts = storage.load_parts()
        query = query.strip().lower()

        for p in parts:
            pid = p.get("part_id", "")
            name = p.get("name", "")
            qty = int(p.get("quantity", 0))
            price = float(p.get("unit_price", 0.0))

            if query:
                if query not in pid.lower() and query not in name.lower():
                    continue

            status_text = "LOW STOCK!" if qty <= LOW_STOCK_THRESHOLD else "In Stock"
            tree.insert("", "end", values=(
                pid,
                name,
                qty,
                f"{price:,.2f}",
                status_text
            ))

    def on_search_change(event=None):
        refresh_table(search_entry.get())

    search_entry.bind("<KeyRelease>", on_search_change)

    # Add / Edit Dialog
    def open_part_dialog(part_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = part_to_edit is not None
        title_text = "Edit Part" if is_edit else "Add New Part"
        dialog.title(title_text)
        dialog.geometry("380x260")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Part Name:").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(form, width=25)
        name_entry.grid(row=0, column=1, pady=6, padx=(10, 0))

        ttk.Label(form, text="Stock Quantity:").grid(row=1, column=0, sticky="w", pady=6)
        qty_spin = ttk.Spinbox(form, from_=0, to=9999, width=23)
        qty_spin.grid(row=1, column=1, pady=6, padx=(10, 0))
        qty_spin.set(0)

        ttk.Label(form, text="Unit Price (PHP):").grid(row=2, column=0, sticky="w", pady=6)
        price_entry = ttk.Entry(form, width=25)
        price_entry.grid(row=2, column=1, pady=6, padx=(10, 0))

        if is_edit:
            name_entry.insert(0, part_to_edit.get("name", ""))
            qty_spin.set(part_to_edit.get("quantity", 0))
            price_entry.insert(0, str(part_to_edit.get("unit_price", 0.0)))

        name_entry.focus()

        def save_part():
            name = name_entry.get().strip()
            qty_str = qty_spin.get().strip()
            price_str = price_entry.get().strip()

            if not validators.is_non_empty(name):
                messagebox.showerror("Validation Error", "Part name is required.", parent=dialog)
                return
            if not validators.is_valid_quantity(qty_str):
                messagebox.showerror("Validation Error", "Please enter a valid stock quantity.", parent=dialog)
                return
            if not validators.is_valid_price(price_str):
                messagebox.showerror("Validation Error", "Please enter a valid unit price.", parent=dialog)
                return

            qty = int(qty_str)
            price = float(price_str)
            parts = storage.load_parts()

            if is_edit:
                pid = part_to_edit["part_id"]
                for p in parts:
                    if p.get("part_id") == pid:
                        p["name"] = name
                        p["quantity"] = qty
                        p["unit_price"] = price
                        break
                storage.save_parts(parts)
                messagebox.showinfo("Success", "Part updated successfully.", parent=dialog)
            else:
                new_id = models.generate_id("PRT-", parts, "part_id")
                new_part = {
                    "part_id": new_id,
                    "name": name,
                    "quantity": qty,
                    "unit_price": price
                }
                parts.append(new_part)
                storage.save_parts(parts)
                messagebox.showinfo("Success", f"Part {new_id} added successfully.", parent=dialog)

            dialog.destroy()
            refresh_table(search_entry.get())

        btn_row = ttk.Frame(form)
        btn_row.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_row, text="Save", command=save_part).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def on_add():
        open_part_dialog()

    def on_edit():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a part to edit.")
            return
        pid = tree.item(selected[0], "values")[0]
        parts = storage.load_parts()
        part = next((p for p in parts if p.get("part_id") == pid), None)
        if part:
            open_part_dialog(part)

    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a part to delete.")
            return
        pid = tree.item(selected[0], "values")[0]
        name = tree.item(selected[0], "values")[1]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete part '{name}' ({pid})?")
        if not confirm:
            return

        parts = storage.load_parts()
        updated = [p for p in parts if p.get("part_id") != pid]
        storage.save_parts(updated)
        messagebox.showinfo("Deleted", f"Part '{name}' has been deleted.")
        refresh_table(search_entry.get())

    role = current_user.get("role", "")
    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", pady=(10, 0))

    if role in ["Admin", "Staff"]:
        ttk.Button(btn_bar, text="Add New Part", command=on_add).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="Edit Part", command=on_edit).pack(side="left", padx=5)

    if role == "Admin":
        ttk.Button(btn_bar, text="Delete Part", command=on_delete).pack(side="left", padx=5)

    # Initial load
    refresh_table()

    # Warn if any part is low in stock (FR-35)
    parts = storage.load_parts()
    low_stock = [p for p in parts if int(p.get("quantity", 0)) <= LOW_STOCK_THRESHOLD]
    if low_stock:
        names = ", ".join([f"{p['name']} ({p['quantity']})" for p in low_stock[:3]])
        if len(low_stock) > 3:
            names += f", and {len(low_stock) - 3} more"
        messagebox.showwarning("Low Stock Warning", f"The following parts have low stock (<= {LOW_STOCK_THRESHOLD}):\n{names}")

    return frame
