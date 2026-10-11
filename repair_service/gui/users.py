# User accounts management module (Admin only) with modern table styling

import tkinter as tk
from tkinter import ttk, messagebox
import storage
import models
import validators
import gui.theme as theme


def show_users_frame(parent, current_user):
    """
    Renders user accounts table and restyled add/edit dialogs for Admin.
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

    columns = ("user_id", "username", "role", "full_name", "customer_id")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("user_id", text="User ID")
    tree.heading("username", text="Username")
    tree.heading("role", text="Role")
    tree.heading("full_name", text="Full Name")
    tree.heading("customer_id", text="Linked Customer ID")

    tree.column("user_id", width=100, anchor="center")
    tree.column("username", width=150)
    tree.column("role", width=120, anchor="center")
    tree.column("full_name", width=220)
    tree.column("customer_id", width=130, anchor="center")

    theme.setup_treeview_tags(tree)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    empty_label = ttk.Label(
        card,
        text="No user accounts found.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        users = storage.load_users()
        query = query.strip().lower()
        displayed_count = 0

        for idx, u in enumerate(users):
            uid = u.get("user_id", "")
            uname = u.get("username", "")
            urole = u.get("role", "")
            fname = u.get("full_name", "")
            cid = u.get("customer_id", "")

            if query:
                if (query not in uid.lower() and
                    query not in uname.lower() and
                    query not in fname.lower() and
                    query not in cid.lower()):
                    continue

            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(uid, uname, urole, fname, cid or "—"), tags=(tag,))
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    search_entry.bind("<KeyRelease>", lambda e: refresh_table(search_entry.get()))

    # Add / Edit Dialog
    def open_user_dialog(user_to_edit=None):
        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        is_edit = user_to_edit is not None
        title_text = "Edit User Account" if is_edit else "Add New User Account"
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
        name_entry = ttk.Entry(grid, width=26)
        name_entry.grid(row=0, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Username *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        uname_entry = ttk.Entry(grid, width=26)
        uname_entry.grid(row=1, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="Password *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        pwd_entry = ttk.Entry(grid, width=26, show="*")
        pwd_entry.grid(row=2, column=1, sticky="e", pady=6, padx=(10, 0))

        ttk.Label(grid, text="System Role *:", style="Surface.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        role_combo = ttk.Combobox(grid, values=["Admin", "Staff", "Technician"], state="readonly", width=24)
        role_combo.grid(row=3, column=1, sticky="e", pady=6, padx=(10, 0))
        role_combo.current(1)

        if is_edit:
            name_entry.insert(0, user_to_edit.get("full_name", ""))
            uname_entry.insert(0, user_to_edit.get("username", ""))
            pwd_entry.insert(0, user_to_edit.get("password", ""))
            role_combo.set(user_to_edit.get("role", "Staff"))

        name_entry.focus()

        def save_user():
            fname = name_entry.get().strip()
            uname = uname_entry.get().strip()
            pwd = pwd_entry.get().strip()
            urole = role_combo.get()

            if not validators.is_non_empty(fname):
                messagebox.showerror("Validation Error", "Full name is required.", parent=dialog)
                return
            if not validators.is_non_empty(uname):
                messagebox.showerror("Validation Error", "Username is required.", parent=dialog)
                return
            if not validators.is_non_empty(pwd):
                messagebox.showerror("Validation Error", "Password is required.", parent=dialog)
                return

            users = storage.load_users()

            for u in users:
                if u.get("username").lower() == uname.lower():
                    if is_edit and u.get("user_id") == user_to_edit.get("user_id"):
                        continue
                    messagebox.showerror("Duplicate Username", f"Username '{uname}' already exists.", parent=dialog)
                    return

            if is_edit:
                uid = user_to_edit["user_id"]
                for u in users:
                    if u.get("user_id") == uid:
                        u["full_name"] = fname
                        u["username"] = uname
                        u["password"] = pwd
                        u["role"] = urole
                        break
                storage.save_users(users)
                messagebox.showinfo("Success", "User account updated successfully.", parent=dialog)
            else:
                new_id = models.generate_id("USR-", users, "user_id")
                new_user = {
                    "user_id": new_id,
                    "username": uname,
                    "password": pwd,
                    "role": urole,
                    "full_name": fname,
                    "customer_id": ""
                }
                users.append(new_user)
                storage.save_users(users)
                messagebox.showinfo("Success", f"User {new_id} created successfully.", parent=dialog)

            dialog.destroy()
            refresh_table(search_entry.get())

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(20, 0))

        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Save User", style="Primary.TButton", command=save_user).pack(side="right")

    def on_add():
        open_user_dialog()

    def on_edit():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account to edit.")
            return
        uid = tree.item(selected[0], "values")[0]
        users = storage.load_users()
        user = next((u for u in users if u.get("user_id") == uid), None)
        if user:
            open_user_dialog(user)

    def on_delete():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user account to delete.")
            return
        uid = tree.item(selected[0], "values")[0]
        uname = tree.item(selected[0], "values")[1]

        if uid == current_user.get("user_id"):
            messagebox.showerror("Action Denied", "You cannot delete your own logged-in account.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user account '{uname}' ({uid})?")
        if not confirm:
            return

        users = storage.load_users()
        updated = [u for u in users if u.get("user_id") != uid]
        storage.save_users(updated)
        messagebox.showinfo("Deleted", f"User account '{uname}' deleted.")
        refresh_table(search_entry.get())

    ttk.Button(btn_bar, text="Add User", style="Primary.TButton", command=on_add).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Edit User", style="Secondary.TButton", command=on_edit).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Delete User", style="Secondary.TButton", command=on_delete).pack(side="left")

    refresh_table()
    return card
