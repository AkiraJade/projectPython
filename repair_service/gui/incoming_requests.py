# Incoming Online Requests management for Staff and Admin

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import storage
import models
import validators


def show_incoming_requests_frame(parent, current_user):
    """
    Renders incoming online requests waiting for device drop-off.
    Staff inspects device upon arrival, enters intake details, and marks Received.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        header_frame,
        text="Incoming Online Requests (Pending Drop-off)",
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

    columns = ("job_id", "customer_name", "contact_no", "device", "problem", "date_submitted")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("customer_name", text="Customer Name")
    tree.heading("contact_no", text="Contact No")
    tree.heading("device", text="Device")
    tree.heading("problem", text="Problem Description")
    tree.heading("date_submitted", text="Date Submitted")

    tree.column("job_id", width=90, anchor="center")
    tree.column("customer_name", width=150)
    tree.column("contact_no", width=110)
    tree.column("device", width=160)
    tree.column("problem", width=220)
    tree.column("date_submitted", width=140, anchor="center")

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    def get_customer_map():
        customers = storage.load_customers()
        return {c["customer_id"]: c for c in customers}

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        cust_map = get_customer_map()
        query = query.strip().lower()

        # Only list Pending Drop-off requests
        pending_dropoffs = [j for j in jobs if j.get("status") == "Pending Drop-off"]

        for j in pending_dropoffs:
            jid = j.get("job_id", "")
            cid = j.get("customer_id", "")
            cinfo = cust_map.get(cid, {})
            cname = cinfo.get("name", "Unknown")
            ccontact = cinfo.get("contact_no", "")
            dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
            prob = j.get("problem", "")
            d_sub = j.get("date_submitted", "")

            if query:
                if (query not in jid.lower() and
                    query not in cname.lower() and
                    query not in dev.lower()):
                    continue

            tree.insert("", "end", values=(jid, cname, ccontact, dev, prob, d_sub))

    def on_search_change(event=None):
        refresh_table(search_entry.get())

    search_entry.bind("<KeyRelease>", on_search_change)

    # Intake dialog when customer drops off the device
    def open_intake_dialog():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an incoming request to process drop-off intake.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid), None)
        if not job:
            return

        cust_map = get_customer_map()
        cinfo = cust_map.get(job.get("customer_id"), {})

        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.title(f"Device Drop-off Intake - {jid}")
        dialog.geometry("540x600")
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

        # Customer Header info
        header_box = ttk.LabelFrame(scroll_frame, text="Customer Information", padding=10)
        header_box.pack(fill="x", pady=(0, 10))

        ttk.Label(header_box, text=f"Customer: {cinfo.get('name', 'N/A')} ({job.get('customer_id')})", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(header_box, text=f"Contact No: {cinfo.get('contact_no', 'N/A')}").pack(anchor="w")
        ttk.Label(header_box, text=f"Reported Problem: {job.get('problem')}").pack(anchor="w")

        # Physical Inspection & Serial Number
        insp_box = ttk.LabelFrame(scroll_frame, text="Physical Inspection & Hardware Details", padding=10)
        insp_box.pack(fill="x", pady=(0, 10))

        ttk.Label(insp_box, text="Serial Number:").grid(row=0, column=0, sticky="w", pady=4)
        serial_entry = ttk.Entry(insp_box, width=28)
        serial_entry.grid(row=0, column=1, sticky="w", pady=4, padx=(10, 0))
        serial_entry.insert(0, job.get("serial_no", ""))

        ttk.Label(insp_box, text="Physical Condition:").grid(row=1, column=0, sticky="w", pady=4)
        cond_entry = ttk.Entry(insp_box, width=28)
        cond_entry.grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))
        cond_entry.insert(0, "Good / Normal wear")

        # Actual accessories received
        ttk.Label(insp_box, text="Accessories Received:").grid(row=2, column=0, sticky="nw", pady=4)
        acc_frame = ttk.Frame(insp_box)
        acc_frame.grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        initial_acc = job.get("accessories", [])
        charger_var = tk.BooleanVar(value="Charger / Adapter" in initial_acc or "Charger/Adapter" in initial_acc)
        bag_var = tk.BooleanVar(value="Bag / Pouch" in initial_acc or "Bag/Pouch" in initial_acc)
        mouse_var = tk.BooleanVar(value="Mouse" in initial_acc)
        cable_var = tk.BooleanVar(value="Power Cable" in initial_acc)

        ttk.Checkbutton(acc_frame, text="Charger / Adapter", variable=charger_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Bag / Pouch", variable=bag_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Mouse", variable=mouse_var).pack(anchor="w")
        ttk.Checkbutton(acc_frame, text="Power Cable", variable=cable_var).pack(anchor="w")

        # Priority & Est Completion
        sched_box = ttk.LabelFrame(scroll_frame, text="Repair Scheduling", padding=10)
        sched_box.pack(fill="x", pady=(0, 10))

        prio_row = ttk.Frame(sched_box)
        prio_row.pack(fill="x", pady=4)
        ttk.Label(prio_row, text="Priority:").pack(side="left")
        prio_var = tk.StringVar(value="Normal")
        ttk.Radiobutton(prio_row, text="Normal", variable=prio_var, value="Normal").pack(side="left", padx=10)
        ttk.Radiobutton(prio_row, text="Urgent", variable=prio_var, value="Urgent").pack(side="left", padx=10)

        est_row = ttk.Frame(sched_box)
        est_row.pack(fill="x", pady=4)
        ttk.Label(est_row, text="Est. Completion:").pack(side="left")
        est_entry = ttk.Entry(est_row, width=15)
        est_entry.pack(side="left", padx=(10, 0))
        est_entry.insert(0, (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"))

        # Attach Services
        serv_box = ttk.LabelFrame(scroll_frame, text="Initial Services", padding=10)
        serv_box.pack(fill="x", pady=(0, 10))

        all_services = storage.load_services()
        serv_listbox = tk.Listbox(serv_box, selectmode="multiple", height=4, exportselection=False)
        for s in all_services:
            serv_listbox.insert(tk.END, f"{s['service_id']} - {s['name']} (PHP {float(s.get('price', 0)):,.2f})")
        serv_listbox.pack(fill="x")
        # Pre-select diagnostic by default
        if len(all_services) > 0:
            serv_listbox.select_set(0)

        # Assign Technician
        tech_box = ttk.LabelFrame(scroll_frame, text="Assign Technician", padding=10)
        tech_box.pack(fill="x", pady=(0, 10))

        all_users = storage.load_users()
        tech_list = [u for u in all_users if u.get("role") == "Technician"]
        tech_options = ["Unassigned"] + [f"{t['user_id']} - {t.get('full_name', t['username'])}" for t in tech_list]
        tech_combo = ttk.Combobox(tech_box, values=tech_options, state="readonly", width=35)
        tech_combo.pack(fill="x")
        tech_combo.current(0)

        def confirm_receipt():
            condition = cond_entry.get().strip()
            if not validators.is_non_empty(condition):
                messagebox.showerror("Validation Error", "Physical condition description is required.", parent=dialog)
                return

            acc_received = []
            if charger_var.get():
                acc_received.append("Charger / Adapter")
            if bag_var.get():
                acc_received.append("Bag / Pouch")
            if mouse_var.get():
                acc_received.append("Mouse")
            if cable_var.get():
                acc_received.append("Power Cable")

            selected_indices = serv_listbox.curselection()
            chosen_service_ids = [all_services[i]["service_id"] for i in selected_indices]

            tech_sel = tech_combo.get()
            tech_id = ""
            if tech_sel != "Unassigned":
                tech_id = tech_sel.split(" - ")[0]

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update job record to Received
            job["serial_no"] = serial_entry.get().strip()
            job["condition"] = condition
            job["accessories"] = acc_received
            job["priority"] = prio_var.get()
            job["est_completion"] = est_entry.get().strip()
            job["services"] = chosen_service_ids
            job["technician_id"] = tech_id
            job["date_received"] = now_str
            job["status"] = "Received"

            if "status_history" not in job:
                job["status_history"] = []
            job["status_history"].append(models.create_status_log(jid, "Received"))

            all_jobs = storage.load_jobs()
            for idx, item in enumerate(all_jobs):
                if item.get("job_id") == jid:
                    all_jobs[idx] = job
                    break
            storage.save_jobs(all_jobs)

            messagebox.showinfo(
                "Device Received",
                f"Device for Job {jid} has been confirmed as Received!\nStatus updated to 'Received'.",
                parent=dialog
            )
            dialog.destroy()
            refresh_table()

        btn_row = ttk.Frame(scroll_frame)
        btn_row.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_row, text="Confirm Receipt (Mark Received)", command=confirm_receipt).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

    def cancel_request():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a request to cancel.")
            return

        jid = tree.item(selected[0], "values")[0]
        cname = tree.item(selected[0], "values")[1]

        reason_win = tk.Toplevel(parent)
        reason_win.transient(parent.winfo_toplevel())
        reason_win.grab_set()
        reason_win.title(f"Cancel Request - {jid}")
        reason_win.geometry("380x200")
        reason_win.resizable(False, False)

        rframe = ttk.Frame(reason_win, padding=20)
        rframe.pack(fill="both", expand=True)

        ttk.Label(rframe, text=f"Cancel Request {jid} for {cname}?", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(rframe, text="Cancellation Reason (e.g. Never brought in):").pack(anchor="w")

        reason_entry = ttk.Entry(rframe, width=35)
        reason_entry.pack(fill="x", pady=6)
        reason_entry.insert(0, "Device never dropped off / cancelled by staff")
        reason_entry.focus()

        def do_cancel():
            reason = reason_entry.get().strip() or "Cancelled by staff"
            jobs = storage.load_jobs()
            for j in jobs:
                if j.get("job_id") == jid:
                    j["status"] = "Cancelled"
                    j["notes"] = (j.get("notes", "") + f" [Cancelled: {reason}]").strip()
                    if "status_history" not in j:
                        j["status_history"] = []
                    j["status_history"].append(models.create_status_log(jid, "Cancelled"))
                    break
            storage.save_jobs(jobs)
            messagebox.showinfo("Cancelled", f"Request {jid} has been cancelled.", parent=reason_win)
            reason_win.destroy()
            refresh_table()

        r_btn_row = ttk.Frame(rframe)
        r_btn_row.pack(fill="x", pady=(15, 0))
        ttk.Button(r_btn_row, text="Confirm Cancellation", command=do_cancel).pack(side="left", padx=5)
        ttk.Button(r_btn_row, text="Close", command=reason_win.destroy).pack(side="left", padx=5)

    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", pady=(10, 0))

    ttk.Button(btn_bar, text="Receive Device (Intake)", command=open_intake_dialog).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="Cancel Request", command=cancel_request).pack(side="left", padx=5)

    refresh_table()
    return frame
