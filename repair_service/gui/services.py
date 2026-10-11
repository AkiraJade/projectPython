# Service catalog management screen module with modern table styling

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators
import gui.theme as theme


def show_services_frame(parent, current_user):
    """
    Renders service catalog list and actions inside a modern card.
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

    # Table with Treeview
    table_frame = ttk.Frame(card, style="Surface.TFrame")
    table_frame.pack(fill="both", expand=True)

    columns = ("service_id", "name", "description", "price")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("service_id", text="Service ID")
    tree.heading("name", text="Service Name")
    tree.heading("description", text="Description")
    tree.heading("price", text="Price (PHP)")

    tree.column("service_id", width=110, anchor="center")
    tree.column("name", width=200)
    tree.column("description", width=340)
    tree.column("price", width=120, anchor="e")

    theme.setup_treeview_tags(tree)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    empty_label = ttk.Label(
        card,
        text="No services found in catalog.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        services = storage.load_services()
        query = query.strip().lower()
        displayed_count = 0

        for idx, s in enumerate(services):
            sid = s.get("service_id", "")
            name = s.get("name", "")
            desc = s.get("description", "")
            price = float(s.get("price", 0.0))

            if query:
                if query not in sid.lower() and query not in name.lower() and query not in desc.lower():
                    continue

            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(sid, name, desc, f"{price:,.2f}"), tags=(tag,))
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    search_entry.bind("<KeyRelease>", lambda e: refresh_table(search_entry.get()))

    # Add / Edit dialog
    def open_service_dialog(service_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = service_to_edit is not None
        title_text = "Edit Service" if is_edit else "Add New Service"
        dialog.title(title_text)
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 440, 300, 400, 260)
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, style="Surface.TFrame", padding=24)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=title_text, style="Surface.TLabel", font=theme.FONT_SECTION).pack(anchor="w")
        ttk.Label(form, text="Fields marked with * are required.", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 14))

        grid = ttk.Frame(form, style="Surface.TFrame")
        grid.pack(fill="x")

        ttk.Label(grid, text="Service Name *:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        name_entry = ttk.Entry(grid, width=26)
        name_entry.grid(row=0, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Description:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        desc_entry = ttk.Entry(grid, width=26)
        desc_entry.grid(row=1, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Price (PHP) *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        price_entry = ttk.Entry(grid, width=26)
        price_entry.grid(row=2, column=1, sticky="e", pady=6, padx=(10, 0))

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

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Save Service", style="Primary.TButton", command=save_service).pack(side="right")

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

    # Buttons for Admin
    user_role = current_user.get("role", "")
    if user_role == "Admin":
        ttk.Button(btn_bar, text="Add Service", style="Primary.TButton", command=on_add).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Edit Service", style="Secondary.TButton", command=on_edit).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bar, text="Delete Service", style="Secondary.TButton", command=on_delete).pack(side="left")

    refresh_table()
    return card
