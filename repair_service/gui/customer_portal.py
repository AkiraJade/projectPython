# Customer Portal module with modern dashboard card styling

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import storage
import models
import validators
import gui.theme as theme


def show_new_request_frame(parent, current_user, on_success_callback=None):
    """
    Form for a customer to submit a new online repair request inside a modern card.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=20)
    card.pack(fill="both", expand=True)

    ttk.Label(
        card,
        text="Submit New Repair Request",
        style="Surface.TLabel",
        font=theme.FONT_SECTION
    ).pack(anchor="w")

    ttk.Label(
        card,
        text="Fill in your device details. Once submitted, bring your device to our shop for intake inspection.",
        style="SurfaceMuted.TLabel"
    ).pack(anchor="w", pady=(2, 14))

    # Form card container
    form_box = ttk.LabelFrame(card, text="Device & Problem Details", padding=16)
    form_box.pack(fill="both", expand=True)

    grid = ttk.Frame(form_box, style="Surface.TFrame")
    grid.pack(fill="x", pady=(0, 10))

    # Device Type
    ttk.Label(grid, text="Device Type *:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
    dev_type_combo = ttk.Combobox(grid, values=["Laptop", "Desktop", "All-in-One"], state="readonly", width=26)
    dev_type_combo.grid(row=0, column=1, sticky="w", pady=6, padx=(12, 0))
    dev_type_combo.current(0)

    # Brand
    ttk.Label(grid, text="Brand *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
    brand_entry = ttk.Entry(grid, width=28)
    brand_entry.grid(row=1, column=1, sticky="w", pady=6, padx=(12, 0))

    # Model
    ttk.Label(grid, text="Model *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
    model_entry = ttk.Entry(grid, width=28)
    model_entry.grid(row=2, column=1, sticky="w", pady=6, padx=(12, 0))

    # Serial Number (optional)
    ttk.Label(grid, text="Serial Number (Optional):", style="Surface.TLabel").grid(row=3, column=0, sticky="w", pady=6)
    serial_entry = ttk.Entry(grid, width=28)
    serial_entry.grid(row=3, column=1, sticky="w", pady=6, padx=(12, 0))

    # Accessories to bring
    ttk.Label(grid, text="Accessories to bring:", style="Surface.TLabel").grid(row=4, column=0, sticky="nw", pady=6)
    acc_frame = ttk.Frame(grid, style="Surface.TFrame")
    acc_frame.grid(row=4, column=1, sticky="w", pady=6, padx=(12, 0))

    charger_var = tk.BooleanVar()
    bag_var = tk.BooleanVar()
    mouse_var = tk.BooleanVar()
    cable_var = tk.BooleanVar()

    ttk.Checkbutton(acc_frame, text="Charger / Adapter", variable=charger_var).pack(anchor="w")
    ttk.Checkbutton(acc_frame, text="Bag / Pouch", variable=bag_var).pack(anchor="w")
    ttk.Checkbutton(acc_frame, text="Mouse", variable=mouse_var).pack(anchor="w")
    ttk.Checkbutton(acc_frame, text="Power Cable", variable=cable_var).pack(anchor="w")

    # Problem description
    ttk.Label(grid, text="Problem Description *:", style="Surface.TLabel").grid(row=5, column=0, sticky="nw", pady=6)
    prob_text = tk.Text(grid, height=5, width=48, font=theme.FONT_BODY)
    prob_text.grid(row=5, column=1, sticky="w", pady=6, padx=(12, 0))

    def submit_request():
        dev_type = dev_type_combo.get().strip()
        brand = brand_entry.get().strip()
        model = model_entry.get().strip()
        serial = serial_entry.get().strip()
        problem = prob_text.get("1.0", tk.END).strip()

        if not validators.is_non_empty(brand):
            messagebox.showerror("Validation Error", "Please enter the device brand.")
            return
        if not validators.is_non_empty(model):
            messagebox.showerror("Validation Error", "Please enter the device model.")
            return
        if not validators.is_non_empty(problem):
            messagebox.showerror("Validation Error", "Please describe the problem.")
            return

        acc_list = []
        if charger_var.get():
            acc_list.append("Charger / Adapter")
        if bag_var.get():
            acc_list.append("Bag / Pouch")
        if mouse_var.get():
            acc_list.append("Mouse")
        if cable_var.get():
            acc_list.append("Power Cable")

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        jobs = storage.load_jobs()
        new_job_id = models.generate_id("JOB-", jobs, "job_id")

        new_job = {
            "job_id": new_job_id,
            "customer_id": current_user.get("customer_id", ""),
            "device_type": dev_type,
            "brand": brand,
            "model": model,
            "serial_no": serial,
            "accessories": acc_list,
            "condition": "Pending Inspection",
            "problem": problem,
            "priority": "Normal",
            "est_completion": "TBD upon drop-off",
            "date_submitted": now_str,
            "date_received": "",
            "technician_id": "",
            "status": "Pending Drop-off",
            "source": "Online",
            "diagnosis": "",
            "notes": "",
            "services": [],
            "parts_used": [],
            "status_history": [
                models.create_status_log(new_job_id, "Pending Drop-off")
            ]
        }

        jobs.append(new_job)
        storage.save_jobs(jobs)

        messagebox.showinfo(
            "Request Submitted",
            f"Your repair request has been submitted!\n\n"
            f"Job ID: {new_job_id}\n"
            f"Status: Pending Drop-off\n\n"
            f"REMINDER:\nPlease bring your device and checked accessories to our repair shop to complete the intake inspection."
        )

        if on_success_callback:
            on_success_callback()

    btn_row = ttk.Frame(card, style="Surface.TFrame")
    btn_row.pack(fill="x", pady=(14, 0))

    ttk.Button(btn_row, text="Submit Request", style="Primary.TButton", command=submit_request).pack(side="left")

    return card


def show_my_requests_frame(parent, current_user):
    """
    Shows a styled table of the customer's own jobs, with details and cancellation options.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    card.pack(fill="both", expand=True)

    toolbar = ttk.Frame(card, style="Surface.TFrame")
    toolbar.pack(fill="x", pady=(0, 12))

    btn_bar = ttk.Frame(toolbar, style="Surface.TFrame")
    btn_bar.pack(side="left")

    # Table Container
    table_frame = ttk.Frame(card, style="Surface.TFrame")
    table_frame.pack(fill="both", expand=True)

    columns = ("job_id", "device", "date_submitted", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("device", text="Device Description")
    tree.heading("date_submitted", text="Date Submitted")
    tree.heading("status", text="Current Status")

    tree.column("job_id", width=110, anchor="center")
    tree.column("device", width=260)
    tree.column("date_submitted", width=160, anchor="center")
    tree.column("status", width=160, anchor="center")

    theme.setup_treeview_tags(tree)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    my_cust_id = current_user.get("customer_id", "")

    empty_label = ttk.Label(
        card,
        text="You have no active repair requests. Click 'New Request' to get started.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        my_jobs = [j for j in jobs if j.get("customer_id") == my_cust_id]

        for idx, j in enumerate(my_jobs):
            jid = j.get("job_id", "")
            dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
            d_sub = j.get("date_submitted", j.get("date_received", ""))
            stat = j.get("status", "")

            zebra_tag = "even" if idx % 2 == 0 else "odd"
            status_tag = f"status_{stat}"
            tree.insert("", "end", values=(jid, dev, d_sub, stat), tags=(zebra_tag, status_tag))

        if len(my_jobs) == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    def view_details():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a request to view details.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid and j.get("customer_id") == my_cust_id), None)
        if not job:
            return

        all_services = storage.load_services()
        service_map = {s["service_id"]: s for s in all_services}
        all_parts = storage.load_parts()
        all_payments = storage.load_payments()

        total = models.compute_job_total(job, all_services, all_parts)
        paid = models.compute_payments_total(jid, all_payments)
        balance = models.compute_balance(job, all_services, all_parts, all_payments)

        win = tk.Toplevel(parent)
        win.transient(parent.winfo_toplevel())
        win.title(f"Request Details - {jid}")
        win.configure(bg=theme.BG_SURFACE)
        theme.center_window(win, 620, 560, 540, 500)

        txt_frame = ttk.Frame(win, style="Surface.TFrame", padding=20)
        txt_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(txt_frame, font=theme.FONT_MONO, bg=theme.BG_SURFACE, relief="solid", borderwidth=1)
        scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        lines = []
        lines.append("=" * 55)
        lines.append(f"REPAIR REQUEST: {jid}")
        lines.append("=" * 55)
        lines.append(f"Current Status:     {job.get('status')}")
        lines.append(f"Date Submitted:     {job.get('date_submitted')}")
        lines.append(f"Date Received:      {job.get('date_received') or 'Not yet dropped off'}")
        lines.append(f"Device:             {job.get('brand')} {job.get('model')} ({job.get('device_type')})")
        lines.append(f"Serial No:          {job.get('serial_no') or 'N/A'}")
        lines.append(f"Condition:          {job.get('condition')}")
        acc_text = ", ".join(job.get("accessories", [])) or "None"
        lines.append(f"Accessories:        {acc_text}")
        lines.append("-" * 55)
        lines.append(f"Problem Description:\n  {job.get('problem')}")
        lines.append("-" * 55)
        lines.append("DIAGNOSIS & NOTES:")
        lines.append(f"  Diagnosis:        {job.get('diagnosis') or 'Pending'}")
        lines.append(f"  Repair Notes:     {job.get('notes') or 'None'}")
        lines.append("-" * 55)
        lines.append("SERVICES:")
        if not job.get("services"):
            lines.append("  (No services added yet)")
        else:
            for sid in job.get("services"):
                s = service_map.get(sid, {})
                sname = s.get("name", sid)
                sprice = float(s.get("price", 0.0))
                lines.append(f"  - {sname:<32} PHP {sprice:,.2f}")
        lines.append("-" * 55)
        lines.append(f"TOTAL BILL:         PHP {total:,.2f}")
        lines.append(f"TOTAL PAID:         PHP {paid:,.2f}")
        lines.append(f"REMAINING BALANCE:  PHP {balance:,.2f}")
        lines.append("-" * 55)
        lines.append("STATUS HISTORY:")
        for log in job.get("status_history", []):
            lines.append(f"  [{log.get('timestamp')}] {log.get('status')}")
        lines.append("=" * 55)

        text_widget.insert(tk.END, "\n".join(lines))
        text_widget.configure(state="disabled")

        btn_box = ttk.Frame(win, style="Surface.TFrame", padding=(20, 0, 20, 16))
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Close", style="Secondary.TButton", command=win.destroy).pack(side="right")

    def cancel_request():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a request to cancel.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid and j.get("customer_id") == my_cust_id), None)
        if not job:
            return

        if job.get("status") != "Pending Drop-off":
            messagebox.showwarning(
                "Cancellation Blocked",
                f"Request {jid} is currently '{job.get('status')}'.\n\n"
                "Customers can only cancel a request while it is 'Pending Drop-off'.\n"
                "Once your device has arrived at the shop, please contact staff directly."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Cancel",
            f"Are you sure you want to cancel repair request {jid}?"
        )
        if not confirm:
            return

        job["status"] = "Cancelled"
        if "status_history" not in job:
            job["status_history"] = []
        job["status_history"].append(models.create_status_log(jid, "Cancelled"))

        storage.save_jobs(jobs)
        messagebox.showinfo("Cancelled", f"Request {jid} has been cancelled.")
        refresh_table()

    ttk.Button(btn_bar, text="View Details", style="Secondary.TButton", command=view_details).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Cancel Request", style="Danger.TButton", command=cancel_request).pack(side="left")

    refresh_table()
    return card


def show_my_receipts_frame(parent, current_user):
    """
    Shows paid jobs and official receipts for the logged-in customer in a modern card.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    card.pack(fill="both", expand=True)

    toolbar = ttk.Frame(card, style="Surface.TFrame")
    toolbar.pack(fill="x", pady=(0, 12))

    btn_bar = ttk.Frame(toolbar, style="Surface.TFrame")
    btn_bar.pack(side="left")

    table_frame = ttk.Frame(card, style="Surface.TFrame")
    table_frame.pack(fill="both", expand=True)

    columns = ("job_id", "device", "total_bill", "total_paid", "balance", "status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("device", text="Device Description")
    tree.heading("total_bill", text="Total Bill (PHP)")
    tree.heading("total_paid", text="Paid (PHP)")
    tree.heading("balance", text="Balance (PHP)")
    tree.heading("status", text="Payment Status")

    tree.column("job_id", width=100, anchor="center")
    tree.column("device", width=220)
    tree.column("total_bill", width=130, anchor="e")
    tree.column("total_paid", width=130, anchor="e")
    tree.column("balance", width=130, anchor="e")
    tree.column("status", width=140, anchor="center")

    theme.setup_treeview_tags(tree)
    tree.tag_configure("fully_paid", foreground=theme.COLOR_SUCCESS, font=theme.FONT_BODY_BOLD)
    tree.tag_configure("balance_due", foreground=theme.COLOR_WARNING, font=theme.FONT_BODY_BOLD)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    my_cust_id = current_user.get("customer_id", "")

    empty_label = ttk.Label(
        card,
        text="No invoices or receipts found for your account.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        all_services = storage.load_services()
        all_parts = storage.load_parts()
        all_payments = storage.load_payments()

        my_jobs = [j for j in jobs if j.get("customer_id") == my_cust_id]
        displayed_count = 0

        for idx, j in enumerate(my_jobs):
            jid = j.get("job_id", "")
            dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
            total = models.compute_job_total(j, all_services, all_parts)
            paid = models.compute_payments_total(jid, all_payments)
            balance = models.compute_balance(j, all_services, all_parts, all_payments)

            if total > 0 or paid > 0:
                p_status = "Fully Paid" if balance <= 0.0 else "Balance Due"
                zebra_tag = "even" if idx % 2 == 0 else "odd"
                pay_tag = "fully_paid" if balance <= 0.0 else "balance_due"

                tree.insert("", "end", values=(
                    jid,
                    dev,
                    f"{total:,.2f}",
                    f"{paid:,.2f}",
                    f"{balance:,.2f}",
                    p_status
                ), tags=(zebra_tag, pay_tag))
                displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    def view_receipt():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a job order to view its receipt.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid and j.get("customer_id") == my_cust_id), None)
        if not job:
            return

        customers = storage.load_customers()
        cust = next((c for c in customers if c.get("customer_id") == my_cust_id), {})

        all_services = storage.load_services()
        service_map = {s["service_id"]: s for s in all_services}
        all_parts = storage.load_parts()
        parts_map = {p["part_id"]: p for p in all_parts}
        all_payments = storage.load_payments()
        job_payments = [p for p in all_payments if p.get("job_id") == jid]

        total_bill = models.compute_job_total(job, all_services, all_parts)
        total_paid = models.compute_payments_total(jid, all_payments)
        balance = models.compute_balance(job, all_services, all_parts, all_payments)

        rec_win = tk.Toplevel(parent)
        rec_win.transient(parent.winfo_toplevel())
        rec_win.title(f"Receipt - {jid}")
        rec_win.configure(bg=theme.BG_SURFACE)
        theme.center_window(rec_win, 620, 580, 560, 500)

        txt_frame = ttk.Frame(rec_win, style="Surface.TFrame", padding=20)
        txt_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(txt_frame, font=theme.FONT_MONO, bg=theme.BG_SURFACE, relief="solid", borderwidth=1)
        scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        lines = []
        lines.append("=" * 55)
        lines.append("       COMPUTER & LAPTOP REPAIR SERVICE")
        lines.append("              OFFICIAL RECEIPT / INVOICE")
        lines.append("=" * 55)
        lines.append(f"Date:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Job Order:       {jid}")
        lines.append(f"Customer Name:   {cust.get('name', 'N/A')}")
        lines.append(f"Device:          {job.get('brand')} {job.get('model')} ({job.get('device_type')})")
        lines.append("-" * 55)
        lines.append("PARTICULARS                          AMOUNT (PHP)")
        lines.append("-" * 55)
        for sid in job.get("services", []):
            s = service_map.get(sid, {})
            lines.append(f"  {s.get('name', sid):<34} {float(s.get('price', 0.0)):>12,.2f}")
        for jp in job.get("parts_used", []):
            p = parts_map.get(jp.get("part_id"), {})
            qty = int(jp.get("quantity_used", 0))
            cost = qty * float(p.get("unit_price", 0.0))
            lines.append(f"  {p.get('name', 'Part')} x{qty:<26} {cost:>12,.2f}")
        lines.append("-" * 55)
        lines.append(f"TOTAL BILL:                            PHP {total_bill:>10,.2f}")
        lines.append("-" * 55)
        lines.append("PAYMENTS:")
        for p in job_payments:
            lines.append(f"  [{p.get('date')}] {p.get('method')}: PHP {float(p.get('amount', 0)):,.2f}")
        lines.append("-" * 55)
        lines.append(f"TOTAL PAID:                            PHP {total_paid:>10,.2f}")
        lines.append(f"BALANCE DUE:                           PHP {balance:>10,.2f}")
        lines.append("=" * 55)

        full_text = "\n".join(lines)
        text_widget.insert(tk.END, full_text)
        text_widget.configure(state="disabled")

        def export_receipt():
            try:
                export_dir = os.path.join(storage.BASE_DIR, "exports")
                if not os.path.exists(export_dir):
                    os.makedirs(export_dir)
                filepath = os.path.join(export_dir, f"my_receipt_{jid}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full_text)
                messagebox.showinfo("Exported", f"Receipt exported to:\n{filepath}", parent=rec_win)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save receipt: {e}", parent=rec_win)

        btn_box = ttk.Frame(rec_win, style="Surface.TFrame", padding=(20, 0, 20, 16))
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Close", style="Secondary.TButton", command=rec_win.destroy).pack(side="left")
        ttk.Button(btn_box, text="Export as .txt", style="Primary.TButton", command=export_receipt).pack(side="right")

    ttk.Button(btn_bar, text="View Official Receipt", style="Primary.TButton", command=view_receipt).pack(side="left")

    refresh_table()
    return card


def show_profile_frame(parent, current_user):
    """
    Profile management: edit own details and change password in a clean card layout.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=24)
    card.pack(fill="both", expand=True)

    ttk.Label(
        card,
        text="Account Profile & Settings",
        style="Surface.TLabel",
        font=theme.FONT_SECTION
    ).pack(anchor="w")

    ttk.Label(
        card,
        text="Manage your contact information and change your password.",
        style="SurfaceMuted.TLabel"
    ).pack(anchor="w", pady=(2, 16))

    customers = storage.load_customers()
    my_cust_id = current_user.get("customer_id", "")
    customer = next((c for c in customers if c.get("customer_id") == my_cust_id), None)

    # 1. Contact Information Card
    profile_box = ttk.LabelFrame(card, text="Contact Details", padding=16)
    profile_box.pack(fill="x", pady=(0, 16))

    grid1 = ttk.Frame(profile_box, style="Surface.TFrame")
    grid1.pack(fill="x")

    ttk.Label(grid1, text="Customer ID:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Label(grid1, text=my_cust_id, style="Surface.TLabel", font=theme.FONT_BODY_BOLD).grid(row=0, column=1, sticky="w", pady=6, padx=(12, 0))

    ttk.Label(grid1, text="Full Name *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
    name_entry = ttk.Entry(grid1, width=32)
    name_entry.grid(row=1, column=1, sticky="w", pady=6, padx=(12, 0))
    name_entry.insert(0, customer.get("name", "") if customer else current_user.get("full_name", ""))

    ttk.Label(grid1, text="Contact No *:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
    contact_entry = ttk.Entry(grid1, width=32)
    contact_entry.grid(row=2, column=1, sticky="w", pady=6, padx=(12, 0))
    contact_entry.insert(0, customer.get("contact_no", "") if customer else "")

    ttk.Label(grid1, text="Email Address *:", style="Surface.TLabel").grid(row=3, column=0, sticky="w", pady=6)
    email_entry = ttk.Entry(grid1, width=32)
    email_entry.grid(row=3, column=1, sticky="w", pady=6, padx=(12, 0))
    email_entry.insert(0, customer.get("email", "") if customer else "")

    ttk.Label(grid1, text="Address *:", style="Surface.TLabel").grid(row=4, column=0, sticky="w", pady=6)
    address_entry = ttk.Entry(grid1, width=32)
    address_entry.grid(row=4, column=1, sticky="w", pady=6, padx=(12, 0))
    address_entry.insert(0, customer.get("address", "") if customer else "")

    # 2. Password Change Section
    pwd_box = ttk.LabelFrame(card, text="Change Password (Optional)", padding=16)
    pwd_box.pack(fill="x", pady=(0, 20))

    grid2 = ttk.Frame(pwd_box, style="Surface.TFrame")
    grid2.pack(fill="x")

    ttk.Label(grid2, text="Current Password:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
    curr_pwd_entry = ttk.Entry(grid2, width=28, show="*")
    curr_pwd_entry.grid(row=0, column=1, sticky="w", pady=6, padx=(12, 0))

    ttk.Label(grid2, text="New Password:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
    new_pwd_entry = ttk.Entry(grid2, width=28, show="*")
    new_pwd_entry.grid(row=1, column=1, sticky="w", pady=6, padx=(12, 0))

    ttk.Label(grid2, text="Confirm New Password:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
    confirm_pwd_entry = ttk.Entry(grid2, width=28, show="*")
    confirm_pwd_entry.grid(row=2, column=1, sticky="w", pady=6, padx=(12, 0))

    def save_profile():
        new_name = name_entry.get().strip()
        new_contact = contact_entry.get().strip()
        new_email = email_entry.get().strip()
        new_address = address_entry.get().strip()

        if not validators.is_non_empty(new_name):
            messagebox.showerror("Validation Error", "Full Name is required.")
            return
        if not validators.is_valid_phone(new_contact):
            messagebox.showerror("Validation Error", "Please enter a valid contact number (at least 7 digits).")
            return
        if not validators.is_valid_email(new_email):
            messagebox.showerror("Validation Error", "Please enter a valid email address.")
            return
        if not validators.is_non_empty(new_address):
            messagebox.showerror("Validation Error", "Address is required.")
            return

        curr_pwd = curr_pwd_entry.get().strip()
        new_pwd = new_pwd_entry.get().strip()
        confirm_pwd = confirm_pwd_entry.get().strip()

        change_pwd = False
        if curr_pwd or new_pwd or confirm_pwd:
            if curr_pwd != current_user.get("password"):
                messagebox.showerror("Validation Error", "Current password does not match.")
                return
            if not validators.is_non_empty(new_pwd):
                messagebox.showerror("Validation Error", "New password cannot be empty.")
                return
            if new_pwd != confirm_pwd:
                messagebox.showerror("Validation Error", "New password and confirmation do not match.")
                return
            change_pwd = True

        all_custs = storage.load_customers()
        for c in all_custs:
            if c.get("customer_id") == my_cust_id:
                c["name"] = new_name
                c["contact_no"] = new_contact
                c["email"] = new_email
                c["address"] = new_address
                break
        storage.save_customers(all_custs)

        all_users = storage.load_users()
        for u in all_users:
            if u.get("user_id") == current_user.get("user_id"):
                u["full_name"] = new_name
                if change_pwd:
                    u["password"] = new_pwd
                    current_user["password"] = new_pwd
                break
        storage.save_users(all_users)

        current_user["full_name"] = new_name
        curr_pwd_entry.delete(0, tk.END)
        new_pwd_entry.delete(0, tk.END)
        confirm_pwd_entry.delete(0, tk.END)

        messagebox.showinfo("Success", "Profile updated successfully.")

    btn_row = ttk.Frame(card, style="Surface.TFrame")
    btn_row.pack(fill="x")
    ttk.Button(btn_row, text="Save Changes", style="Primary.TButton", command=save_profile).pack(side="left")

    return card
