# Parts inventory management module with modern table styling

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators
import gui.theme as theme

LOW_STOCK_THRESHOLD = 3


def show_parts_frame(parent, current_user):
    """
    Renders parts inventory table, search, and restyled add/edit dialogs.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    card.pack(fill="both", expand=True)

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

    columns = ("part_id", "name", "quantity", "unit_price", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("part_id", text="Part ID")
    tree.heading("name", text="Part Name")
    tree.heading("quantity", text="Stock Qty")
    tree.heading("unit_price", text="Unit Price (PHP)")
    tree.heading("status", text="Stock Status")

    tree.column("part_id", width=100, anchor="center")
    tree.column("name", width=300)
    tree.column("quantity", width=100, anchor="center")
    tree.column("unit_price", width=140, anchor="e")
    tree.column("status", width=140, anchor="center")

    theme.setup_treeview_tags(tree)
    tree.tag_configure("low_stock", foreground=theme.COLOR_WARNING, font=theme.FONT_BODY_BOLD)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    empty_label = ttk.Label(
        card,
        text="No parts found in inventory.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        parts = storage.load_parts()
        query = query.strip().lower()
        displayed_count = 0

        for idx, p in enumerate(parts):
            pid = p.get("part_id", "")
            name = p.get("name", "")
            qty = int(p.get("quantity", 0))
            price = float(p.get("unit_price", 0.0))

            if query:
                if query not in pid.lower() and query not in name.lower():
                    continue

            is_low = qty <= LOW_STOCK_THRESHOLD
            status_text = "LOW STOCK!" if is_low else "In Stock"

            zebra_tag = "even" if idx % 2 == 0 else "odd"
            tag_list = (zebra_tag, "low_stock") if is_low else (zebra_tag,)

            tree.insert("", "end", values=(
                pid,
                name,
                qty,
                f"{price:,.2f}",
                status_text
            ), tags=tag_list)
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    search_entry.bind("<KeyRelease>", lambda e: refresh_table(search_entry.get()))

    # Add / Edit Dialog
    def open_part_dialog(part_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = part_to_edit is not None
        title_text = "Edit Part" if is_edit else "Add New Part"
        dialog.title(title_text)
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 440, 310, 400, 270)
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, style="Surface.TFrame", padding=24)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=title_text, style="Surface.TLabel", font=theme.FONT_SECTION).pack(anchor="w")
        ttk.Label(form, text="Fields marked with * are required.", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 14))

        grid = ttk.Frame(form, style="Surface.TFrame")
        grid.pack(fill="x")

        ttk.Label(grid, text="Part Name *:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(grid, width=26)
        name_entry.grid(row=0, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Stock Quantity *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        qty_spin = ttk.Spinbox(grid, from_=0, to=9999, width=24)
        qty_spin.grid(row=1, column=1, sticky="e", pady=6, padx=(10, 0))
        qty_spin.set(0)

        ttk.Label(grid, text="Unit Price (PHP) *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        price_entry = ttk.Entry(grid, width=26)
        price_entry.grid(row=2, column=1, sticky="e", pady=6, padx=(10, 0))

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

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Save Part", style="Primary.TButton", command=save_part).pack(side="right")

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
    if role in ["Admin", "Staff"]:
        ttk.Button(btn_bar, text="Add New Part", style="Primary.TButton", command=on_add).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Edit Part", style="Secondary.TButton", command=on_edit).pack(side="left", padx=(0, 6))

    if role == "Admin":
        ttk.Button(btn_bar, text="Delete Part", style="Secondary.TButton", command=on_delete).pack(side="left")

    refresh_table()
    return card
