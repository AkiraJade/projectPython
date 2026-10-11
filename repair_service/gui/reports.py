# Reports, analytics dashboard, backup and export module

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import csv
import storage
import models


def show_reports_frame(parent, current_user):
    """
    Renders reports dashboard: status counts, pending jobs, sales breakdown, and data backup.
    """
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))

    ttk.Label(
        header_frame,
        text="Reports & System Dashboard",
        font=("Arial", 14, "bold")
    ).pack(side="left")

    # Data loading and computations
    jobs = storage.load_jobs()
    payments = storage.load_payments()
    customers = storage.load_customers()
    cust_map = {c["customer_id"]: c.get("name", "Unknown") for c in customers}

    # Status counts (FR-43)
    status_counts = {s: 0 for s in models.STATUS_LIST}
    for j in jobs:
        st = j.get("status", "Received")
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1

    total_jobs = len(jobs)
    pending_jobs = [j for j in jobs if j.get("status") in models.ACTIVE_STATUSES]

    # Sales calculations (FR-44)
    today_str = datetime.now().strftime("%Y-%m-%d")
    month_str = datetime.now().strftime("%Y-%m")

    total_revenue = 0.0
    today_sales = 0.0
    month_sales = 0.0
    method_totals = {"Cash": 0.0, "GCash": 0.0, "Card": 0.0}

    for p in payments:
        amt = float(p.get("amount", 0.0))
        p_date = p.get("date", "")
        method = p.get("method", "Cash")

        total_revenue += amt
        if p_date.startswith(today_str):
            today_sales += amt
        if p_date.startswith(month_str):
            month_sales += amt

        if method in method_totals:
            method_totals[method] += amt
        else:
            method_totals[method] = amt

    # Top Metrics Cards Row
    metrics_frame = ttk.LabelFrame(frame, text="Key Metrics Overview", padding=10)
    metrics_frame.pack(fill="x", pady=(0, 10))

    col0 = ttk.Frame(metrics_frame)
    col0.grid(row=0, column=0, padx=15, sticky="w")
    ttk.Label(col0, text="Total Jobs:", font=("Arial", 9)).pack(anchor="w")
    ttk.Label(col0, text=str(total_jobs), font=("Arial", 14, "bold")).pack(anchor="w")

    col1 = ttk.Frame(metrics_frame)
    col1.grid(row=0, column=1, padx=15, sticky="w")
    ttk.Label(col1, text="Active / Pending:", font=("Arial", 9)).pack(anchor="w")
    ttk.Label(col1, text=str(len(pending_jobs)), font=("Arial", 14, "bold"), foreground="orange").pack(anchor="w")

    col2 = ttk.Frame(metrics_frame)
    col2.grid(row=0, column=2, padx=15, sticky="w")
    ttk.Label(col2, text="Today's Sales:", font=("Arial", 9)).pack(anchor="w")
    ttk.Label(col2, text=f"PHP {today_sales:,.2f}", font=("Arial", 14, "bold")).pack(anchor="w")

    col3 = ttk.Frame(metrics_frame)
    col3.grid(row=0, column=3, padx=15, sticky="w")
    ttk.Label(col3, text="This Month's Sales:", font=("Arial", 9)).pack(anchor="w")
    ttk.Label(col3, text=f"PHP {month_sales:,.2f}", font=("Arial", 14, "bold")).pack(anchor="w")

    col4 = ttk.Frame(metrics_frame)
    col4.grid(row=0, column=4, padx=15, sticky="w")
    ttk.Label(col4, text="Total Revenue:", font=("Arial", 9)).pack(anchor="w")
    ttk.Label(col4, text=f"PHP {total_revenue:,.2f}", font=("Arial", 14, "bold"), foreground="green").pack(anchor="w")

    # Status Breakdown summary line
    stat_box = ttk.LabelFrame(frame, text="Jobs by Status Breakdown", padding=10)
    stat_box.pack(fill="x", pady=(0, 10))

    stat_line = ttk.Frame(stat_box)
    stat_line.pack(fill="x")
    for idx, (st, count) in enumerate(status_counts.items()):
        ttk.Label(stat_line, text=f"{st}: {count}", font=("Arial", 9, "bold")).grid(row=idx // 4, column=idx % 4, padx=12, pady=3, sticky="w")

    # Pending Jobs Table (FR-45)
    pending_box = ttk.LabelFrame(frame, text=f"Pending Jobs List ({len(pending_jobs)} items)", padding=10)
    pending_box.pack(fill="both", expand=True, pady=(0, 10))

    columns = ("job_id", "customer", "device", "priority", "status", "date_received", "est_completion")
    tree = ttk.Treeview(pending_box, columns=columns, show="headings", height=5)

    tree.heading("job_id", text="Job ID")
    tree.heading("customer", text="Customer")
    tree.heading("device", text="Device")
    tree.heading("priority", text="Priority")
    tree.heading("status", text="Status")
    tree.heading("date_received", text="Date Received")
    tree.heading("est_completion", text="Est. Completion")

    tree.column("job_id", width=80, anchor="center")
    tree.column("customer", width=150)
    tree.column("device", width=160)
    tree.column("priority", width=80, anchor="center")
    tree.column("status", width=110, anchor="center")
    tree.column("date_received", width=120, anchor="center")
    tree.column("est_completion", width=110, anchor="center")

    scroll_y = ttk.Scrollbar(pending_box, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    for j in pending_jobs:
        jid = j.get("job_id", "")
        cid = j.get("customer_id", "")
        cname = cust_map.get(cid, cid)
        dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
        tree.insert("", "end", values=(
            jid,
            cname,
            dev,
            j.get("priority", ""),
            j.get("status", ""),
            j.get("date_received", ""),
            j.get("est_completion", "")
        ))

    # Export Functions (FR-46)
    def export_sales_csv():
        try:
            export_dir = os.path.join(storage.BASE_DIR, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            fpath = os.path.join(export_dir, filename)

            with open(fpath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Payment ID", "Job ID", "Date", "Method", "Amount (PHP)"])
                for p in payments:
                    writer.writerow([
                        p.get("payment_id", ""),
                        p.get("job_id", ""),
                        p.get("date", ""),
                        p.get("method", ""),
                        f"{float(p.get('amount', 0)):.2f}"
                    ])
                writer.writerow([])
                writer.writerow(["SUMMARY", "", "", "", ""])
                writer.writerow(["Today's Sales", f"{today_sales:.2f}"])
                writer.writerow(["Month's Sales", f"{month_sales:.2f}"])
                writer.writerow(["Total Revenue", f"{total_revenue:.2f}"])

            messagebox.showinfo("Export Success", f"Sales report exported to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def export_summary_txt():
        try:
            export_dir = os.path.join(storage.BASE_DIR, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            fpath = os.path.join(export_dir, filename)

            lines = []
            lines.append("=" * 60)
            lines.append("       COMPUTER & LAPTOP REPAIR SERVICE SYSTEM")
            lines.append("                 SYSTEM SUMMARY REPORT")
            lines.append("=" * 60)
            lines.append(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("-" * 60)
            lines.append("1. JOBS SUMMARY")
            lines.append(f"   Total Jobs Recorded: {total_jobs}")
            lines.append(f"   Active / Pending:    {len(pending_jobs)}")
            lines.append("   Breakdown by Status:")
            for st, cnt in status_counts.items():
                lines.append(f"     - {st:<20}: {cnt}")
            lines.append("-" * 60)
            lines.append("2. FINANCIAL & SALES SUMMARY")
            lines.append(f"   Today's Sales:       PHP {today_sales:,.2f}")
            lines.append(f"   This Month's Sales:  PHP {month_sales:,.2f}")
            lines.append(f"   Total Gross Revenue: PHP {total_revenue:,.2f}")
            lines.append("   Breakdown by Payment Method:")
            for m, total_m in method_totals.items():
                lines.append(f"     - {m:<20}: PHP {total_m:,.2f}")
            lines.append("-" * 60)
            lines.append("3. PENDING JOBS DETAIL")
            for j in pending_jobs:
                cid = j.get("customer_id", "")
                cname = cust_map.get(cid, cid)
                dev = f"{j.get('brand', '')} {j.get('model', '')}".strip()
                lines.append(f"   * [{j.get('job_id')}] {cname} | {dev} | {j.get('status')} | Est: {j.get('est_completion')}")
            lines.append("=" * 60)

            with open(fpath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            messagebox.showinfo("Export Success", f"Summary report exported to:\n{fpath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export TXT: {e}")

    def perform_backup():
        bpath = storage.backup_data()
        if bpath:
            messagebox.showinfo("Backup Completed", f"All data files successfully backed up to:\n{bpath}")

    # Actions Bar (FR-46, FR-50)
    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x", pady=(5, 0))

    ttk.Button(btn_bar, text="Export Sales Report (.csv)", command=export_sales_csv).pack(side="left", padx=5)
    ttk.Button(btn_bar, text="Export Summary Report (.txt)", command=export_summary_txt).pack(side="left", padx=5)

    if current_user.get("role") == "Admin":
        ttk.Button(btn_bar, text="Backup Data Files", command=perform_backup).pack(side="left", padx=5)

    return frame
