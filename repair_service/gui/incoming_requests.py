# Incoming Online Requests management for Staff and Admin with modern styling

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import storage
import models
import validators
import gui.theme as theme


def show_incoming_requests_frame(parent, current_user):
    """
    Renders incoming online requests waiting for device drop-off inside a modern card.
    Staff inspects device upon arrival, enters intake details, and marks Received.
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

    columns = ("job_id", "customer_name", "contact_no", "device", "problem", "date_submitted")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("customer_name", text="Customer Name")
    tree.heading("contact_no", text="Contact No")
    tree.heading("device", text="Device Description")
    tree.heading("problem", text="Problem Description")
    tree.heading("date_submitted", text="Date Submitted")

    tree.column("job_id", width=95, anchor="center")
    tree.column("customer_name", width=160)
    tree.column("contact_no", width=120)
    tree.column("device", width=180)
    tree.column("problem", width=250)
    tree.column("date_submitted", width=150, anchor="center")

    theme.setup_treeview_tags(tree)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    empty_label = ttk.Label(
        card,
        text="No incoming online requests pending drop-off.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def get_customer_map():
        customers = storage.load_customers()
        return {c["customer_id"]: c for c in customers}

    def refresh_table(query=""):
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        cust_map = get_customer_map()
        query = query.strip().lower()
        displayed_count = 0

        pending_dropoffs = [j for j in jobs if j.get("status") == "Pending Drop-off"]

        for idx, j in enumerate(pending_dropoffs):
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

            tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end", values=(jid, cname, ccontact, dev, prob, d_sub), tags=(tag, "status_Pending Drop-off"))
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    search_entry.bind("<KeyRelease>", lambda e: refresh_table(search_entry.get()))

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
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 600, 660, 540, 580)
        dialog.resizable(False, False)

        canvas = tk.Canvas(dialog, bg=theme.BG_SURFACE, highlightthickness=0)
        scroll = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Surface.TFrame", padding=24)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        ttk.Label(scroll_frame, text=f"Intake Inspection: {jid}", style="Surface.TLabel", font=theme.FONT_TITLE).pack(anchor="w")
        ttk.Label(scroll_frame, text="Confirm received accessories, record condition, and attach services.", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 14))

        # Customer Header info
        header_box = ttk.LabelFrame(scroll_frame, text="Customer Information", padding=14)
        header_box.pack(fill="x", pady=(0, 12))

        ttk.Label(header_box, text=f"Customer: {cinfo.get('name', 'N/A')} ({job.get('customer_id')})", style="Surface.TLabel", font=theme.FONT_BODY_BOLD).pack(anchor="w")
        ttk.Label(header_box, text=f"Contact No: {cinfo.get('contact_no', 'N/A')}", style="SurfaceMuted.TLabel").pack(anchor="w", pady=2)
        ttk.Label(header_box, text=f"Reported Problem: {job.get('problem')}", style="Surface.TLabel").pack(anchor="w", pady=(4, 0))

        # Physical Inspection & Serial Number
        insp_box = ttk.LabelFrame(scroll_frame, text="Physical Inspection & Hardware Details", padding=14)
        insp_box.pack(fill="x", pady=(0, 12))

        ttk.Label(insp_box, text="Serial Number:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        serial_entry = ttk.Entry(insp_box, width=30)
        serial_entry.grid(row=0, column=1, sticky="w", pady=4, padx=(10, 0))
        serial_entry.insert(0, job.get("serial_no", ""))

        ttk.Label(insp_box, text="Physical Condition *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        cond_entry = ttk.Entry(insp_box, width=30)
        cond_entry.grid(row=1, column=1, sticky="w", pady=4, padx=(10, 0))
        cond_entry.insert(0, "Good / Normal wear")

        ttk.Label(insp_box, text="Accessories Received:", style="Surface.TLabel").grid(row=2, column=0, sticky="nw", pady=4)
        acc_frame = ttk.Frame(insp_box, style="Surface.TFrame")
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
        sched_box = ttk.LabelFrame(scroll_frame, text="Repair Scheduling", padding=14)
        sched_box.pack(fill="x", pady=(0, 12))

        prio_row = ttk.Frame(sched_box, style="Surface.TFrame")
        prio_row.pack(fill="x", pady=4)
        ttk.Label(prio_row, text="Priority:", style="Surface.TLabel").pack(side="left")
        prio_var = tk.StringVar(value="Normal")
        ttk.Radiobutton(prio_row, text="Normal", variable=prio_var, value="Normal").pack(side="left", padx=10)
        ttk.Radiobutton(prio_row, text="Urgent", variable=prio_var, value="Urgent").pack(side="left", padx=10)

        est_row = ttk.Frame(sched_box, style="Surface.TFrame")
        est_row.pack(fill="x", pady=4)
        ttk.Label(est_row, text="Est. Completion:", style="Surface.TLabel").pack(side="left")
        est_entry = ttk.Entry(est_row, width=15)
        est_entry.pack(side="left", padx=(10, 0))
        est_entry.insert(0, (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"))

        # Attach Services
        serv_box = ttk.LabelFrame(scroll_frame, text="Attach Services", padding=14)
        serv_box.pack(fill="x", pady=(0, 12))

        all_services = storage.load_services()
        serv_listbox = tk.Listbox(serv_box, selectmode="multiple", height=4, font=theme.FONT_BODY, exportselection=False)
        for s in all_services:
            serv_listbox.insert(tk.END, f"{s['service_id']} - {s['name']} (PHP {float(s.get('price', 0)):,.2f})")
        serv_listbox.pack(fill="x")
        if len(all_services) > 0:
            serv_listbox.select_set(0)

        # Assign Technician
        tech_box = ttk.LabelFrame(scroll_frame, text="Assign Technician", padding=14)
        tech_box.pack(fill="x", pady=(0, 14))

        all_users = storage.load_users()
        tech_list = [u for u in all_users if u.get("role") == "Technician"]
        tech_options = ["Unassigned"] + [f"{t['user_id']} - {t.get('full_name', t['username'])}" for t in tech_list]
        tech_combo = ttk.Combobox(tech_box, values=tech_options, state="readonly", width=42)
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
                f"Device for Job {jid} has been marked as Received!\nStatus updated to 'Received'.",
                parent=dialog
            )
            dialog.destroy()
            refresh_table()

        btn_row = ttk.Frame(scroll_frame, style="Surface.TFrame")
        btn_row.pack(fill="x", pady=(10, 10))

        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Confirm Receipt (Mark Received)", style="Primary.TButton", command=confirm_receipt).pack(side="right")

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
        reason_win.configure(bg=theme.BG_SURFACE)
        theme.center_window(reason_win, 420, 220, 380, 200)
        reason_win.resizable(False, False)

        rframe = ttk.Frame(reason_win, style="Surface.TFrame", padding=24)
        rframe.pack(fill="both", expand=True)

        ttk.Label(rframe, text=f"Cancel Request {jid} for {cname}?", style="Surface.TLabel", font=theme.FONT_SECTION).pack(anchor="w")
        ttk.Label(rframe, text="Enter cancellation reason:", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 8))

        reason_entry = ttk.Entry(rframe, width=35)
        reason_entry.pack(fill="x", pady=(0, 16))
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

        r_btn_row = ttk.Frame(rframe, style="Surface.TFrame")
        r_btn_row.pack(fill="x")
        ttk.Button(r_btn_row, text="Close", style="Secondary.TButton", command=reason_win.destroy).pack(side="left")
        ttk.Button(r_btn_row, text="Confirm Cancellation", style="Danger.TButton", command=do_cancel).pack(side="right")

    ttk.Button(btn_bar, text="Receive Device (Intake)", style="Primary.TButton", command=open_intake_dialog).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="Cancel Request", style="Secondary.TButton", command=cancel_request).pack(side="left")

    refresh_table()
    return card
