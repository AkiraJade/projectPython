# Reports, analytics dashboard, backup and export module with modern summary cards

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import csv
import storage
import models
import gui.theme as theme


def show_reports_frame(parent, current_user):
    """
    Renders reports dashboard with modern summary cards, status grid,
    pending jobs table, and export utilities.
    """
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)

    # Data loading and computations
    jobs = storage.load_jobs()
    payments = storage.load_payments()
    customers = storage.load_customers()
    cust_map = {c["customer_id"]: c.get("name", "Unknown") for c in customers}

    status_counts = {s: 0 for s in models.STATUS_LIST}
    for j in jobs:
        st = j.get("status", "Received")
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1

    total_jobs = len(jobs)
    pending_jobs = [j for j in jobs if j.get("status") in models.ACTIVE_STATUSES]

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

    # 1. Top Metrics Cards Row
    metrics_row = ttk.Frame(frame)
    metrics_row.pack(fill="x", pady=(0, 14))

    def make_kpi_card(parent_frame, title_text, value_text, value_color=theme.TEXT_MAIN):
        c = ttk.Frame(parent_frame, style="Card.TFrame", padding=(16, 14))
        c.pack(side="left", fill="both", expand=True, padx=4)

        ttk.Label(c, text=title_text.upper(), style="SurfaceMuted.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        val_lbl = ttk.Label(c, text=value_text, style="Surface.TLabel", font=("Segoe UI", 16, "bold"))
        val_lbl.pack(anchor="w", pady=(4, 0))
        if value_color != theme.TEXT_MAIN:
            val_lbl.configure(foreground=value_color)
        return c

    make_kpi_card(metrics_row, "Total Jobs", str(total_jobs))
    make_kpi_card(metrics_row, "Active / Pending", str(len(pending_jobs)), theme.COLOR_WARNING)
    make_kpi_card(metrics_row, "Today's Revenue", f"PHP {today_sales:,.2f}")
    make_kpi_card(metrics_row, "This Month", f"PHP {month_sales:,.2f}")
    make_kpi_card(metrics_row, "Total Revenue", f"PHP {total_revenue:,.2f}", theme.COLOR_SUCCESS)

    # 2. Status Breakdown Card
    stat_card = ttk.Frame(frame, style="Card.TFrame", padding=(16, 12))
    stat_card.pack(fill="x", pady=(0, 14))

    ttk.Label(stat_card, text="STATUS BREAKDOWN", style="SurfaceMuted.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))

    stat_grid = ttk.Frame(stat_card, style="Surface.TFrame")
    stat_grid.pack(fill="x")

    for idx, (st, count) in enumerate(status_counts.items()):
        badge = ttk.Frame(stat_grid, style="Surface.TFrame")
        badge.grid(row=idx // 4, column=idx % 4, sticky="w", padx=12, pady=3)

        color = theme.STATUS_COLORS.get(st, theme.TEXT_MAIN)
        ttk.Label(badge, text=f"• {st}:", style="Surface.TLabel", font=theme.FONT_BODY).pack(side="left")
        ttk.Label(badge, text=f" {count}", style="Surface.TLabel", font=theme.FONT_BODY_BOLD, foreground=color).pack(side="left")

    # 3. Pending Jobs Table Card
    table_card = ttk.Frame(frame, style="Card.TFrame", padding=16)
    table_card.pack(fill="both", expand=True, pady=(0, 14))

    ttk.Label(table_card, text=f"PENDING JOBS ({len(pending_jobs)})", style="SurfaceMuted.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))

    columns = ("job_id", "customer", "device", "priority", "status", "date_received", "est_completion")
    tree = ttk.Treeview(table_card, columns=columns, show="headings", height=5)

    tree.heading("job_id", text="Job ID")
    tree.heading("customer", text="Customer Name")
    tree.heading("device", text="Device Description")
    tree.heading("priority", text="Priority")
    tree.heading("status", text="Current Status")
    tree.heading("date_received", text="Date Received")
    tree.heading("est_completion", text="Est. Completion")

    tree.column("job_id", width=95, anchor="center")
    tree.column("customer", width=160)
    tree.column("device", width=180)
    tree.column("priority", width=85, anchor="center")
    tree.column("status", width=130, anchor="center")
    tree.column("date_received", width=130, anchor="center")
    tree.column("est_completion", width=120, anchor="center")

    theme.setup_treeview_tags(tree)

    scroll_y = ttk.Scrollbar(table_card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    for idx, j in enumerate(pending_jobs):
        jid = j.get("job_id", "")
        cid = j.get("customer_id", "")
        cname = cust_map.get(cid, cid)
        dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
        st = j.get("status", "")

        zebra_tag = "even" if idx % 2 == 0 else "odd"
        status_tag = f"status_{st}"
        tree.insert("", "end", values=(
            jid,
            cname,
            dev,
            j.get("priority", ""),
            st,
            j.get("date_received", "") or "Pending Drop-off",
            j.get("est_completion", "")
        ), tags=(zebra_tag, status_tag))

    # 4. Export Functions & Actions Bar
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

    btn_bar = ttk.Frame(frame)
    btn_bar.pack(fill="x")

    ttk.Button(btn_bar, text="Export Sales Report (.csv)", style="Primary.TButton", command=export_sales_csv).pack(side="left", padx=(0, 8))
    ttk.Button(btn_bar, text="Export Summary Report (.txt)", style="Secondary.TButton", command=export_summary_txt).pack(side="left", padx=(0, 8))

    if current_user.get("role") == "Admin":
        ttk.Button(btn_bar, text="Backup Data Files", style="Secondary.TButton", command=perform_backup).pack(side="left")

    return frame
