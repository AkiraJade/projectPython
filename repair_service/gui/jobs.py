# Job order creation, tracking, and management module

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
import storage
import models
import validators


def show_jobs_frame(parent, current_user):
    """
    Renders job orders table, status filters, intake form, and status updates.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    is_technician = current_user.get("role") == "Technician"

    # Header and Search/Filter Bar
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    title_text = "My Assigned Jobs" if is_technician else "Job Orders & Repair Tracking"
    ttk.Label(
        header_frame,
        text=title_text,
        font=("Arial", 14, "bold")
    ).pack(side="left")

    controls_frame = ttk.Frame(header_frame)
    controls_frame.pack(side="right")

    ttk.Label(controls_frame, text="Status:").pack(side="left", padx=(0, 4))
    status_filter = ttk.Combobox(
        controls_frame,
        values=["All"] + models.STATUS_LIST,
        state="readonly",
        width=15
    )
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0, 10))

    ttk.Label(controls_frame, text="Search:").pack(side="left", padx=(0, 4))
    search_entry = ttk.Entry(controls_frame, width=18)
    search_entry.pack(side="left")

    # Job Orders Table
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    columns = ("job_id", "customer", "device", "priority", "technician", "status", "date_received")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("customer", text="Customer")
    tree.heading("device", text="Device")
    tree.heading("priority", text="Priority")
    tree.heading("technician", text="Technician")
    tree.heading("status", text="Status")
    tree.heading("date_received", text="Date Received")

    tree.column("job_id", width=90, anchor="center")
    tree.column("customer", width=160)
    tree.column("device", width=170)
    tree.column("priority", width=80, anchor="center")
    tree.column("technician", width=140)
    tree.column("status", width=120, anchor="center")
    tree.column("date_received", width=130, anchor="center")

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # Map of customer IDs to Names for display
    def get_customer_map():
        customers = storage.load_customers()
        return {c["customer_id"]: c.get("name", "Unknown") for c in customers}

    # Map of technician user IDs to full names
    def get_tech_map():
        users = storage.load_users()
        return {u["user_id"]: u.get("full_name", u.get("username")) for u in users}

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        cust_map = get_customer_map()
        tech_map = get_tech_map()

        selected_status = status_filter.get()
        query = search_entry.get().strip().lower()

        for j in jobs:
            # Technician view filter
            if is_technician and j.get("technician_id") != current_user.get("user_id"):
                continue

            jid = j.get("job_id", "")
            cid = j.get("customer_id", "")
            cname = cust_map.get(cid, cid)
            dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
            serial = j.get("serial_no", "")
            priority = j.get("priority", "Normal")
            tid = j.get("technician_id", "")
            tname = tech_map.get(tid, "Unassigned")
            stat = j.get("status", "Received")
            date_rcv = j.get("date_received", "")

            # Filter by status
            if selected_status != "All" and stat != selected_status:
                continue

            # Search filter (Job ID, Customer Name, Serial No)
            if query:
                if (query not in jid.lower() and
                    query not in cname.lower() and
                    query not in serial.lower()):
                    continue

            tree.insert("", "end", values=(jid, cname, dev, priority, tname, stat, date_rcv))

    status_filter.bind("<<ComboboxSelected>>", lambda e: refresh_table())
    search_entry.bind("<KeyRelease>", lambda e: refresh_table())

    # Intake Form Dialog (New Job Order)
    def open_new_job_dialog():
        customers = storage.load_customers()
        if not customers:
            messagebox.showwarning("No Customers", "Please register at least one customer before creating a job order.")
            return

        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.title("New Job Order Intake")
        dialog.geometry("580x640")
        dialog.resizable(False, False)

        canvas = tk.Canvas(dialog)
        scroll = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding=15)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # 1. Customer Section
        cust_box = ttk.LabelFrame(scroll_frame, text="Customer", padding=10)
        cust_box.pack(fill="x", pady=(0, 10))

        cust_options = [f"{c['customer_id']} - {c['name']}" for c in customers]
        ttk.Label(cust_box, text="Select Customer:").grid(row=0, column=0, sticky="w", pady=4)
        cust_combo = ttk.Combobox(cust_box, values=cust_options, state="readonly", width=38)
        cust_combo.grid(row=0, column=1, pady=4, padx=(10, 0))
        cust_combo.current(0)

        # 2. Device Details Section
        dev_box = ttk.LabelFrame(scroll_frame, text="Device Information", padding=10)
        dev_box.pack(fill="x", pady=(0, 10))

        ttk.Label(dev_box, text="Device Type:").grid(row=0, column=0, sticky="w", pady=4)
        dev_type_combo = ttk.Combobox(dev_box, values=["Laptop", "Desktop", "All-in-One"], state="readonly", width=25)
        dev_type_combo.grid(row=0, column=1, sticky="w", pady=4, padx=(10, 0))
        dev_type_combo.current(0)

        ttk.Label(dev_box, text="Brand:").grid(row=1, column=0, sticky="w", pady=4)
        brand_entry = ttk.Entry(dev_box, width=27)
        brand_entry.grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))

        ttk.Label(dev_box, text="Model:").grid(row=2, column=0, sticky="w", pady=4)
        model_entry = ttk.Entry(dev_box, width=27)
        model_entry.grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        ttk.Label(dev_box, text="Serial Number:").grid(row=3, column=0, sticky="w", pady=4)
        serial_entry = ttk.Entry(dev_box, width=27)
        serial_entry.grid(row=3, column=1, sticky="w", pady=4, padx=(10, 0))

        ttk.Label(dev_box, text="Condition on Arrival:").grid(row=4, column=0, sticky="w", pady=4)
        cond_entry = ttk.Entry(dev_box, width=27)
        cond_entry.grid(row=4, column=1, sticky="w", pady=4, padx=(10, 0))
        cond_entry.insert(0, "Good / Normal wear")

        # Accessories Checkbuttons
        ttk.Label(dev_box, text="Accessories:").grid(row=5, column=0, sticky="nw", pady=4)
        acc_frame = ttk.Frame(dev_box)
        acc_frame.grid(row=5, column=1, sticky="w", pady=4, padx=(10, 0))

        charger_var = tk.BooleanVar()
        bag_var = tk.BooleanVar()
        mouse_var = tk.BooleanVar()
        cable_var = tk.BooleanVar()

        ttk.Checkbutton(acc_frame, text="Charger/Adapter", variable=charger_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Bag/Pouch", variable=bag_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Mouse", variable=mouse_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Power Cable", variable=cable_var).pack(anchor="w")

        # 3. Problem and Priority Section
        prob_box = ttk.LabelFrame(scroll_frame, text="Problem & Priority", padding=10)
        prob_box.pack(fill="x", pady=(0, 10))

        ttk.Label(prob_box, text="Problem Description:").pack(anchor="w")
        prob_text = tk.Text(prob_box, height=4, width=50, font=("Arial", 9))
        prob_text.pack(fill="x", pady=(4, 8))

        prio_row = ttk.Frame(prob_box)
        prio_row.pack(fill="x")
        ttk.Label(prio_row, text="Priority:").pack(side="left")
        prio_var = tk.StringVar(value="Normal")
        ttk.Radiobutton(prio_row, text="Normal", variable=prio_var, value="Normal").pack(side="left", padx=10)
        ttk.Radiobutton(prio_row, text="Urgent", variable=prio_var, value="Urgent").pack(side="left", padx=10)

        # Estimated Date
        est_row = ttk.Frame(prob_box)
        est_row.pack(fill="x", pady=(8, 0))
        ttk.Label(est_row, text="Est. Completion:").pack(side="left")
        est_date_entry = ttk.Entry(est_row, width=15)
        est_date_entry.pack(side="left", padx=(10, 0))
        default_est = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        est_date_entry.insert(0, default_est)

        # 4. Services Selection (Multi-select Listbox)
        serv_box = ttk.LabelFrame(scroll_frame, text="Attach Services", padding=10)
        serv_box.pack(fill="x", pady=(0, 10))

        all_services = storage.load_services()
        serv_listbox = tk.Listbox(serv_box, selectmode="multiple", height=5, exportselection=False)
        for s in all_services:
            serv_listbox.insert(tk.END, f"{s['service_id']} - {s['name']} (PHP {float(s.get('price', 0)):,.2f})")
        serv_listbox.pack(fill="x")

        # 5. Technician Assignment
        tech_box = ttk.LabelFrame(scroll_frame, text="Assign Technician", padding=10)
        tech_box.pack(fill="x", pady=(0, 10))

        all_users = storage.load_users()
        tech_list = [u for u in all_users if u.get("role") == "Technician"]
        tech_options = ["Unassigned"] + [f"{t['user_id']} - {t.get('full_name', t['username'])}" for t in tech_list]

        tech_combo = ttk.Combobox(tech_box, values=tech_options, state="readonly", width=38)
        tech_combo.pack(fill="x")
        tech_combo.current(0)

        def save_job_order():
            cust_selection = cust_combo.get()
            cid = cust_selection.split(" - ")[0]

            dev_type = dev_type_combo.get().strip()
            brand = brand_entry.get().strip()
            model = model_entry.get().strip()
            serial = serial_entry.get().strip()
            cond = cond_entry.get().strip()
            problem = prob_text.get("1.0", tk.END).strip()
            priority = prio_var.get()
            est_date = est_date_entry.get().strip()

            if not validators.is_non_empty(brand) or not validators.is_non_empty(model):
                messagebox.showerror("Validation Error", "Device brand and model are required.", parent=dialog)
                return
            if not validators.is_non_empty(problem):
                messagebox.showerror("Validation Error", "Problem description is required.", parent=dialog)
                return

            # Collect accessories
            acc_list = []
            if charger_var.get():
                acc_list.append("Charger/Adapter")
            if bag_var.get():
                acc_list.append("Bag/Pouch")
            if mouse_var.get():
                acc_list.append("Mouse")
            if cable_var.get():
                acc_list.append("Power Cable")

            # Collect selected services
            selected_indices = serv_listbox.curselection()
            chosen_service_ids = [all_services[i]["service_id"] for i in selected_indices]

            # Collect assigned technician
            tech_selection = tech_combo.get()
            tech_id = ""
            if tech_selection != "Unassigned":
                tech_id = tech_selection.split(" - ")[0]

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            jobs = storage.load_jobs()
            new_job_id = models.generate_id("JOB-", jobs, "job_id")

            new_job = {
                "job_id": new_job_id,
                "customer_id": cid,
                "device_type": dev_type,
                "brand": brand,
                "model": model,
                "serial_no": serial,
                "accessories": acc_list,
                "condition": cond,
                "problem": problem,
                "priority": priority,
                "est_completion": est_date,
                "date_submitted": now_str,
                "date_received": now_str,
                "technician_id": tech_id,
                "status": "Received",
                "source": "Walk-in",
                "diagnosis": "",
                "notes": "",
                "services": chosen_service_ids,
                "parts_used": [],
                "status_history": [
                    models.create_status_log(new_job_id, "Received")
                ]
            }

            jobs.append(new_job)
            storage.save_jobs(jobs)

            messagebox.showinfo("Success", f"Job Order {new_job_id} created successfully!", parent=dialog)
            dialog.destroy()
            refresh_table()

            # Offer to view/print receipt immediately (FR-19)
            open_job_details(new_job_id)

        # Dialog Buttons
        btn_row = ttk.Frame(scroll_frame)
        btn_row.pack(fill="x", pady=(15, 10))

        ttk.Button(btn_row, text="Create Job Order", command=save_job_order).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    # Status & Repair Update Dialog
    def open_update_status_dialog():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a job order to update.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = None
        for j in jobs:
            if j.get("job_id") == jid:
                job = j
                break

        if not job:
            return

        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.title(f"Update Job - {jid}")
        dialog.geometry("480x480")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=f"Job Order: {jid}", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # Status selection
        stat_frame = ttk.Frame(form)
        stat_frame.pack(fill="x", pady=5)
        ttk.Label(stat_frame, text="Status:").pack(side="left")
        current_stat = job.get("status", "Received")
        allowed_stats = [current_stat] + [s for s in models.VALID_TRANSITIONS.get(current_stat, []) if s != current_stat]
        status_combo = ttk.Combobox(stat_frame, values=allowed_stats, state="readonly", width=22)
        status_combo.pack(side="left", padx=(15, 0))
        status_combo.set(current_stat)

        # Reassign technician if Admin or Staff
        all_users = storage.load_users()
        tech_list = [u for u in all_users if u.get("role") == "Technician"]
        tech_options = ["Unassigned"] + [f"{t['user_id']} - {t.get('full_name', t['username'])}" for t in tech_list]

        tech_combo = None
        if not is_technician:
            tech_frame = ttk.Frame(form)
            tech_frame.pack(fill="x", pady=5)
            ttk.Label(tech_frame, text="Technician:").pack(side="left")
            tech_combo = ttk.Combobox(tech_frame, values=tech_options, state="readonly", width=26)
            tech_combo.pack(side="left", padx=(5, 0))

            current_tid = job.get("technician_id", "")
            selected_tech_text = "Unassigned"
            for opt in tech_options:
                if opt.startswith(current_tid) and current_tid:
                    selected_tech_text = opt
                    break
            tech_combo.set(selected_tech_text)

        # Diagnosis
        ttk.Label(form, text="Diagnosis:").pack(anchor="w", pady=(8, 2))
        diag_text = tk.Text(form, height=4, width=50, font=("Arial", 9))
        diag_text.pack(fill="x")
        diag_text.insert(tk.END, job.get("diagnosis", ""))

        # Notes
        ttk.Label(form, text="Repair Notes:").pack(anchor="w", pady=(8, 2))
        notes_text = tk.Text(form, height=4, width=50, font=("Arial", 9))
        notes_text.pack(fill="x")
        notes_text.insert(tk.END, job.get("notes", ""))

        def save_updates():
            new_status = status_combo.get()
            old_status = job.get("status")
            diagnosis = diag_text.get("1.0", tk.END).strip()
            notes = notes_text.get("1.0", tk.END).strip()

            # Rule: reject invalid status jumps
            if new_status != old_status and not models.is_valid_transition(old_status, new_status):
                allowed_opts = models.VALID_TRANSITIONS.get(old_status, [])
                messagebox.showerror(
                    "Invalid Status Transition",
                    f"Cannot change status from '{old_status}' to '{new_status}'.\nAllowed transitions: {', '.join(allowed_opts)}",
                    parent=dialog
                )
                return

            # Rule: Cannot mark Released unless balance is 0 (FR-42)
            if new_status == "Released":
                all_services = storage.load_services()
                all_parts = storage.load_parts()
                all_payments = storage.load_payments()
                balance = models.compute_balance(job, all_services, all_parts, all_payments)
                if balance > 0.0:
                    messagebox.showerror(
                        "Release Blocked",
                        f"Cannot mark device as Released because there is an unpaid balance of PHP {balance:,.2f}.\n"
                        "Please process full payment first in the Billing section.",
                        parent=dialog
                    )
                    return

            job["diagnosis"] = diagnosis
            job["notes"] = notes

            if tech_combo:
                tech_sel = tech_combo.get()
                if tech_sel == "Unassigned":
                    job["technician_id"] = ""
                else:
                    job["technician_id"] = tech_sel.split(" - ")[0]

            # If status changed, record timestamp in status_history (FR-29)
            if new_status != old_status:
                job["status"] = new_status
                if "status_history" not in job:
                    job["status_history"] = []
                job["status_history"].append(models.create_status_log(jid, new_status))

            # Save back to storage
            all_jobs = storage.load_jobs()
            for idx, item in enumerate(all_jobs):
                if item.get("job_id") == jid:
                    all_jobs[idx] = job
                    break
            storage.save_jobs(all_jobs)

            # Notification prompt on Completed (FR-32)
            if new_status == "Completed" and old_status != "Completed":
                messagebox.showinfo(
                    "Device Ready",
                    f"Job {jid} is marked Completed!\nPlease contact customer to inform them that the device is ready for pickup.",
                    parent=dialog
                )
            else:
                messagebox.showinfo("Success", f"Job {jid} updated successfully.", parent=dialog)

            dialog.destroy()
            refresh_table()

        btn_row = ttk.Frame(form)
        btn_row.pack(fill="x", pady=(15, 0))
        ttk.Button(btn_row, text="Save Updates", command=save_updates).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    # Job Details / Intake Receipt Viewer (FR-19)
    def open_job_details(target_job_id=None):
        if not target_job_id:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please select a job order to view.")
                return
            target_job_id = tree.item(selected[0], "values")[0]

        jobs = storage.load_jobs()
        job = None
        for j in jobs:
            if j.get("job_id") == target_job_id:
                job = j
                break

        if not job:
            return

        customers = storage.load_customers()
        cust = next((c for c in customers if c["customer_id"] == job.get("customer_id")), {})

        users = storage.load_users()
        tech = next((u for u in users if u["user_id"] == job.get("technician_id")), {})

        all_services = storage.load_services()
        service_map = {s["service_id"]: s for s in all_services}

        all_parts = storage.load_parts()
        all_payments = storage.load_payments()

        # Build text view for job order receipt
        details_win = tk.Toplevel(parent)
        details_win.transient(parent.winfo_toplevel())
        details_win.title(f"Job Order Sheet - {target_job_id}")
        details_win.geometry("560x520")

        txt_frame = ttk.Frame(details_win, padding=15)
        txt_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(txt_frame, font=("Courier New", 10))
        text_scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scroll.set)

        text_widget.pack(side="left", fill="both", expand=True)
        text_scroll.pack(side="right", fill="y")

        # Format details
        lines = []
        lines.append("=" * 55)
        lines.append("       COMPUTER & LAPTOP REPAIR SERVICE")
        lines.append("                 JOB ORDER SHEET")
        lines.append("=" * 55)
        lines.append(f"Job ID:          {job.get('job_id')}")
        lines.append(f"Date Received:   {job.get('date_received')}")
        lines.append(f"Status:          {job.get('status')}")
        lines.append(f"Priority:        {job.get('priority')}")
        lines.append(f"Est. Completion: {job.get('est_completion')}")
        lines.append("-" * 55)
        lines.append("CUSTOMER DETAILS:")
        lines.append(f"Name:            {cust.get('name', 'N/A')}")
        lines.append(f"Contact No.:     {cust.get('contact_no', 'N/A')}")
        lines.append(f"Email:           {cust.get('email', 'N/A')}")
        lines.append(f"Address:         {cust.get('address', 'N/A')}")
        lines.append("-" * 55)
        lines.append("DEVICE DETAILS:")
        lines.append(f"Type:            {job.get('device_type')}")
        lines.append(f"Brand/Model:     {job.get('brand')} {job.get('model')}")
        lines.append(f"Serial No.:      {job.get('serial_no') or 'N/A'}")
        lines.append(f"Condition:       {job.get('condition')}")
        acc_text = ", ".join(job.get("accessories", [])) or "None"
        lines.append(f"Accessories:     {acc_text}")
        lines.append(f"Problem:         {job.get('problem')}")
        lines.append("-" * 55)
        lines.append("ASSIGNED TECHNICIAN & REPAIR:")
        lines.append(f"Technician:      {tech.get('full_name', 'Unassigned')}")
        lines.append(f"Diagnosis:       {job.get('diagnosis') or 'Pending'}")
        lines.append(f"Notes:           {job.get('notes') or 'None'}")
        lines.append("-" * 55)
        lines.append("SERVICES REQUESTED:")
        job_services = job.get("services", [])
        if not job_services:
            lines.append("  (None selected)")
        else:
            for sid in job_services:
                sinfo = service_map.get(sid, {})
                sname = sinfo.get("name", sid)
                sprice = float(sinfo.get("price", 0.0))
                lines.append(f"  - {sname:<30} PHP {sprice:,.2f}")

        total_bill = models.compute_job_total(job, all_services, all_parts)
        paid = models.compute_payments_total(target_job_id, all_payments)
        balance = models.compute_balance(job, all_services, all_parts, all_payments)

        lines.append("-" * 55)
        lines.append(f"Total Estimate:  PHP {total_bill:,.2f}")
        lines.append(f"Total Paid:      PHP {paid:,.2f}")
        lines.append(f"Remaining:       PHP {balance:,.2f}")
        lines.append("-" * 55)
        lines.append("STATUS HISTORY:")
        for log in job.get("status_history", []):
            lines.append(f"  [{log.get('timestamp')}] {log.get('status')}")
        lines.append("=" * 55)

        full_content = "\n".join(lines)
        text_widget.insert(tk.END, full_content)
        text_widget.configure(state="disabled")

        # Export button (.txt export FR-19 / FR-41)
        btn_box = ttk.Frame(details_win, padding=(15, 0, 15, 10))
        btn_box.pack(fill="x")

        def export_txt():
            try:
                export_dir = os.path.join(storage.BASE_DIR, "exports")
                if not os.path.exists(export_dir):
                    os.makedirs(export_dir)
                filepath = os.path.join(export_dir, f"job_{target_job_id}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full_content)
                messagebox.showinfo("Export Successful", f"Job sheet exported to:\n{filepath}", parent=details_win)
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not save file: {e}", parent=details_win)

        ttk.Button(btn_box, text="Export as .txt", command=export_txt).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Close", command=details_win.destroy).pack(side="right", padx=5)

    # Add Part Used to Job Dialog (FR-34, FR-36)
    def open_add_parts_dialog():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a job order to attach replacement parts.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid), None)
        if not job:
            return

        parts = storage.load_parts()
        if not parts:
            messagebox.showinfo("No Parts", "There are no parts in the inventory.")
            return

        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.title(f"Add Part Used - {jid}")
        dialog.geometry("420x240")
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, padding=20)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=f"Attach Part to {jid}", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        part_options = [f"{p['part_id']} - {p['name']} (Stock: {p['quantity']}, PHP {p['unit_price']:,.2f})" for p in parts]

        ttk.Label(form, text="Select Part:").pack(anchor="w")
        part_combo = ttk.Combobox(form, values=part_options, state="readonly", width=42)
        part_combo.pack(fill="x", pady=(2, 10))
        part_combo.current(0)

        qty_row = ttk.Frame(form)
        qty_row.pack(fill="x", pady=(0, 15))
        ttk.Label(qty_row, text="Quantity Used:").pack(side="left")
        qty_spin = ttk.Spinbox(qty_row, from_=1, to=100, width=10)
        qty_spin.pack(side="left", padx=(10, 0))
        qty_spin.set(1)

        def save_part_usage():
            sel_text = part_combo.get()
            pid = sel_text.split(" - ")[0]
            qty_str = qty_spin.get().strip()

            if not validators.is_valid_quantity(qty_str):
                messagebox.showerror("Validation Error", "Please enter a valid positive quantity.", parent=dialog)
                return

            req_qty = int(qty_str)
            if req_qty <= 0:
                messagebox.showerror("Validation Error", "Quantity must be at least 1.", parent=dialog)
                return

            all_parts = storage.load_parts()
            selected_part = next((p for p in all_parts if p.get("part_id") == pid), None)
            if not selected_part:
                return

            curr_stock = int(selected_part.get("quantity", 0))
            if req_qty > curr_stock:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Cannot add part. Requested: {req_qty}, Available in stock: {curr_stock}.",
                    parent=dialog
                )
                return

            # Deduct inventory stock (FR-34)
            selected_part["quantity"] = curr_stock - req_qty
            storage.save_parts(all_parts)

            # Record in job order
            if "parts_used" not in job:
                job["parts_used"] = []

            # Check if part was already listed in job
            found = False
            for pu in job["parts_used"]:
                if pu.get("part_id") == pid:
                    pu["quantity_used"] = int(pu.get("quantity_used", 0)) + req_qty
                    found = True
                    break
            if not found:
                job["parts_used"].append({"part_id": pid, "quantity_used": req_qty})

            all_jobs = storage.load_jobs()
            for idx, item in enumerate(all_jobs):
                if item.get("job_id") == jid:
                    all_jobs[idx] = job
                    break
            storage.save_jobs(all_jobs)

            messagebox.showinfo("Part Added", f"Added {req_qty}x {selected_part['name']} to Job {jid}.\nInventory updated.", parent=dialog)
            dialog.destroy()
            refresh_table()

        btn_row = ttk.Frame(form)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Add Part", command=save_part_usage).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def on_cancel_job():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a job order to cancel.")
            return

        jid = tree.item(selected[0], "values")[0]
        confirm = messagebox.askyesno("Confirm Cancel", f"Are you sure you want to cancel Job Order {jid}?")
        if not confirm:
            return

        jobs = storage.load_jobs()
        for j in jobs:
            if j.get("job_id") == jid:
                j["status"] = "Cancelled"
                if "status_history" not in j:
                    j["status_history"] = []
                j["status_history"].append(models.create_status_log(jid, "Cancelled"))
                break
        storage.save_jobs(jobs)
        messagebox.showinfo("Job Cancelled", f"Job Order {jid} has been cancelled.")
        refresh_table()

    # Bottom Actions Bar
    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", pady=(10, 0))

    if not is_technician:
        ttk.Button(btn_bar, text="New Job Order", command=open_new_job_dialog).pack(side="left", padx=5)

    ttk.Button(btn_bar, text="Update Status & Notes", command=open_update_status_dialog).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="Add Part Used", command=open_add_parts_dialog).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="View Details / Receipt", command=open_job_details).pack(side="left", padx=5)

    if not is_technician:
        ttk.Button(btn_bar, text="Cancel Job", command=on_cancel_job).pack(side="left", padx=5)

    refresh_table()
    return frame
