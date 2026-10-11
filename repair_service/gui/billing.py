# Billing and payment management module with modern UI styling

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import storage
import models
import validators
import gui.theme as theme


def show_billing_frame(parent, current_user):
    """
    Renders billing management: view balances, process payments, and generate official receipts.
    """
    card = ttk.Frame(parent, style="Card.TFrame", padding=16)
    card.pack(fill="both", expand=True)

    toolbar = ttk.Frame(card, style="Surface.TFrame")
    toolbar.pack(fill="x", pady=(0, 12))

    btn_bar = ttk.Frame(toolbar, style="Surface.TFrame")
    btn_bar.pack(side="left")

    controls_frame = ttk.Frame(toolbar, style="Surface.TFrame")
    controls_frame.pack(side="right")

    ttk.Label(controls_frame, text="Payment Status:", style="Surface.TLabel", font=theme.FONT_BODY).pack(side="left", padx=(0, 6))
    pay_filter = ttk.Combobox(
        controls_frame,
        values=["All", "Unpaid / Balance Due", "Fully Paid"],
        state="readonly",
        width=20
    )
    pay_filter.set("All")
    pay_filter.pack(side="left", padx=(0, 12))

    ttk.Label(controls_frame, text="Search:", style="Surface.TLabel", font=theme.FONT_BODY).pack(side="left", padx=(0, 6))
    search_entry = ttk.Entry(controls_frame, width=20)
    search_entry.pack(side="left")

    # Table with Treeview
    table_frame = ttk.Frame(card, style="Surface.TFrame")
    table_frame.pack(fill="both", expand=True)

    columns = ("job_id", "customer", "device", "total_bill", "total_paid", "balance", "job_status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

    tree.heading("job_id", text="Job ID")
    tree.heading("customer", text="Customer Name")
    tree.heading("device", text="Device Description")
    tree.heading("total_bill", text="Total Bill (PHP)")
    tree.heading("total_paid", text="Paid (PHP)")
    tree.heading("balance", text="Balance Due (PHP)")
    tree.heading("job_status", text="Repair Status")

    tree.column("job_id", width=95, anchor="center")
    tree.column("customer", width=170)
    tree.column("device", width=180)
    tree.column("total_bill", width=130, anchor="e")
    tree.column("total_paid", width=130, anchor="e")
    tree.column("balance", width=140, anchor="e")
    tree.column("job_status", width=130, anchor="center")

    theme.setup_treeview_tags(tree)
    tree.tag_configure("fully_paid", foreground=theme.COLOR_SUCCESS, font=theme.FONT_BODY_BOLD)
    tree.tag_configure("balance_due", foreground=theme.COLOR_WARNING, font=theme.FONT_BODY_BOLD)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    empty_label = ttk.Label(
        card,
        text="No billing records found.",
        style="SurfaceMuted.TLabel",
        font=theme.FONT_BODY
    )

    def get_customer_map():
        customers = storage.load_customers()
        return {c["customer_id"]: c.get("name", "Unknown") for c in customers}

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)

        jobs = storage.load_jobs()
        cust_map = get_customer_map()
        all_services = storage.load_services()
        all_parts = storage.load_parts()
        all_payments = storage.load_payments()

        filter_choice = pay_filter.get()
        query = search_entry.get().strip().lower()
        displayed_count = 0

        for idx, j in enumerate(jobs):
            jid = j.get("job_id", "")
            cid = j.get("customer_id", "")
            cname = cust_map.get(cid, cid)
            dev = f"{j.get('brand', '')} {j.get('model', '')}".strip() or j.get("device_type", "")
            jstatus = j.get("status", "")

            total = models.compute_job_total(j, all_services, all_parts)
            paid = models.compute_payments_total(jid, all_payments)
            balance = models.compute_balance(j, all_services, all_parts, all_payments)

            if filter_choice == "Unpaid / Balance Due" and balance <= 0.0:
                continue
            if filter_choice == "Fully Paid" and balance > 0.0:
                continue

            if query:
                if query not in jid.lower() and query not in cname.lower():
                    continue

            zebra_tag = "even" if idx % 2 == 0 else "odd"
            pay_tag = "fully_paid" if balance <= 0.0 else "balance_due"

            tree.insert("", "end", values=(
                jid,
                cname,
                dev,
                f"{total:,.2f}",
                f"{paid:,.2f}",
                f"{balance:,.2f}",
                jstatus
            ), tags=(zebra_tag, pay_tag))
            displayed_count += 1

        if displayed_count == 0:
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            empty_label.place_forget()

    pay_filter.bind("<<ComboboxSelected>>", lambda e: refresh_table())
    search_entry.bind("<KeyRelease>", lambda e: refresh_table())

    # Process Payment Dialog
    def open_payment_dialog():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a job order to process payment.")
            return

        jid = tree.item(selected[0], "values")[0]
        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == jid), None)
        if not job:
            return

        all_services = storage.load_services()
        all_parts = storage.load_parts()
        all_payments = storage.load_payments()

        total = models.compute_job_total(job, all_services, all_parts)
        paid = models.compute_payments_total(jid, all_payments)
        balance = models.compute_balance(job, all_services, all_parts, all_payments)

        if balance <= 0.0:
            messagebox.showinfo("Fully Paid", f"Job Order {jid} is already fully paid! Remaining balance is PHP 0.00.")
            return

        dialog = tk.Toplevel(parent)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.title(f"Process Payment - {jid}")
        dialog.configure(bg=theme.BG_SURFACE)
        theme.center_window(dialog, 480, 460, 420, 400)
        dialog.resizable(False, False)

        form = ttk.Frame(dialog, style="Surface.TFrame", padding=24)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text=f"Payment for Job: {jid}", style="Surface.TLabel", font=theme.FONT_SECTION).pack(anchor="w")
        ttk.Label(form, text="Record client payment and calculate change.", style="SurfaceMuted.TLabel").pack(anchor="w", pady=(2, 14))

        # Balance breakdown display card
        summary_box = ttk.LabelFrame(form, text="Bill Summary", padding=14)
        summary_box.pack(fill="x", pady=(0, 14))

        ttk.Label(summary_box, text=f"Total Bill:        PHP {total:,.2f}", style="Surface.TLabel").pack(anchor="w", pady=2)
        ttk.Label(summary_box, text=f"Already Paid:      PHP {paid:,.2f}", style="SurfaceMuted.TLabel").pack(anchor="w", pady=2)
        bal_label = ttk.Label(summary_box, text=f"Balance Due:       PHP {balance:,.2f}", style="Surface.TLabel", font=theme.FONT_BODY_BOLD, foreground=theme.COLOR_WARNING)
        bal_label.pack(anchor="w", pady=2)

        # Payment inputs
        input_frame = ttk.LabelFrame(form, text="Transaction Details", padding=14)
        input_frame.pack(fill="x", pady=(0, 16))

        ttk.Label(input_frame, text="Payment Amount *:", style="Surface.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        amount_entry = ttk.Entry(input_frame, width=22)
        amount_entry.grid(row=0, column=1, sticky="e", pady=6, padx=(10, 0))
        amount_entry.insert(0, f"{balance:.2f}")

        ttk.Label(input_frame, text="Payment Method *:", style="Surface.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        method_combo = ttk.Combobox(input_frame, values=["Cash", "GCash", "Card"], state="readonly", width=20)
        method_combo.grid(row=1, column=1, sticky="e", pady=6, padx=(10, 0))
        method_combo.current(0)

        ttk.Label(input_frame, text="Cash Tendered:", style="Surface.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        tendered_entry = ttk.Entry(input_frame, width=22)
        tendered_entry.grid(row=2, column=1, sticky="e", pady=6, padx=(10, 0))
        tendered_entry.insert(0, f"{balance:.2f}")

        change_display = ttk.Label(input_frame, text="Change: PHP 0.00", style="SurfaceMuted.TLabel", font=theme.FONT_BODY_BOLD)
        change_display.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

        def update_change(event=None):
            amt_str = amount_entry.get().strip()
            tend_str = tendered_entry.get().strip()
            if validators.is_valid_price(amt_str) and validators.is_valid_price(tend_str):
                amt = float(amt_str)
                tend = float(tend_str)
                diff = tend - amt
                if diff >= 0:
                    change_display.configure(text=f"Change: PHP {diff:,.2f}", foreground=theme.COLOR_SUCCESS)
                else:
                    change_display.configure(text="Change: (Insufficient Cash)", foreground=theme.COLOR_DANGER)
            else:
                change_display.configure(text="Change: PHP 0.00", foreground=theme.TEXT_MUTED)

        amount_entry.bind("<KeyRelease>", update_change)
        tendered_entry.bind("<KeyRelease>", update_change)

        def save_payment():
            amt_str = amount_entry.get().strip()
            method = method_combo.get()
            tend_str = tendered_entry.get().strip()

            if not validators.is_valid_price(amt_str):
                messagebox.showerror("Validation Error", "Please enter a valid payment amount.", parent=dialog)
                return

            pay_amount = float(amt_str)
            if pay_amount <= 0.0:
                messagebox.showerror("Validation Error", "Payment amount must be greater than zero.", parent=dialog)
                return

            if pay_amount > balance:
                messagebox.showerror(
                    "Overpayment",
                    f"Payment amount (PHP {pay_amount:,.2f}) cannot exceed current balance (PHP {balance:,.2f}).",
                    parent=dialog
                )
                return

            change_amount = 0.0
            if method == "Cash":
                if not validators.is_valid_price(tend_str):
                    messagebox.showerror("Validation Error", "Please enter a valid tendered cash amount.", parent=dialog)
                    return
                tendered = float(tend_str)
                if tendered < pay_amount:
                    messagebox.showerror("Validation Error", "Cash tendered is less than payment amount.", parent=dialog)
                    return
                change_amount = tendered - pay_amount

            payments = storage.load_payments()
            new_pay_id = models.generate_id("PAY-", payments, "payment_id")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_payment = {
                "payment_id": new_pay_id,
                "job_id": jid,
                "amount": pay_amount,
                "method": method,
                "date": now_str
            }
            payments.append(new_payment)
            storage.save_payments(payments)

            msg = f"Payment of PHP {pay_amount:,.2f} recorded via {method} ({new_pay_id})."
            if method == "Cash" and change_amount > 0:
                msg += f"\nChange to return: PHP {change_amount:,.2f}"

            messagebox.showinfo("Payment Successful", msg, parent=dialog)
            dialog.destroy()
            refresh_table()
            open_receipt_window(jid)

        btn_row = ttk.Frame(form, style="Surface.TFrame")
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
        ttk.Button(btn_row, text="Confirm Payment", style="Primary.TButton", command=save_payment).pack(side="right")

    # Official Receipt / Invoice Window
    def open_receipt_window(target_job_id=None):
        if not target_job_id:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please select a job order to view receipt.")
                return
            target_job_id = tree.item(selected[0], "values")[0]

        jobs = storage.load_jobs()
        job = next((j for j in jobs if j.get("job_id") == target_job_id), None)
        if not job:
            return

        customers = storage.load_customers()
        cust = next((c for c in customers if c.get("customer_id") == job.get("customer_id")), {})

        all_services = storage.load_services()
        service_map = {s["service_id"]: s for s in all_services}

        all_parts = storage.load_parts()
        parts_map = {p["part_id"]: p for p in all_parts}

        all_payments = storage.load_payments()
        job_payments = [p for p in all_payments if p.get("job_id") == target_job_id]

        receipt_win = tk.Toplevel(parent)
        receipt_win.transient(parent.winfo_toplevel())
        receipt_win.title(f"Official Receipt - {target_job_id}")
        receipt_win.configure(bg=theme.BG_SURFACE)
        theme.center_window(receipt_win, 620, 580, 560, 500)

        txt_frame = ttk.Frame(receipt_win, style="Surface.TFrame", padding=20)
        txt_frame.pack(fill="both", expand=True)

        text_widget = tk.Text(txt_frame, font=theme.FONT_MONO, bg=theme.BG_SURFACE, relief="solid", borderwidth=1)
        text_scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scroll.set)

        text_widget.pack(side="left", fill="both", expand=True)
        text_scroll.pack(side="right", fill="y")

        lines = []
        lines.append("=" * 55)
        lines.append("       COMPUTER & LAPTOP REPAIR SERVICE")
        lines.append("              OFFICIAL RECEIPT / INVOICE")
        lines.append("=" * 55)
        lines.append(f"Receipt Date:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Job Order ID:    {target_job_id}")
        lines.append(f"Customer Name:   {cust.get('name', 'N/A')}")
        lines.append(f"Contact No.:     {cust.get('contact_no', 'N/A')}")
        lines.append(f"Device:          {job.get('brand')} {job.get('model')} ({job.get('device_type')})")
        lines.append(f"Serial No.:      {job.get('serial_no') or 'N/A'}")
        lines.append("-" * 55)
        lines.append("PARTICULARS                          AMOUNT (PHP)")
        lines.append("-" * 55)

        lines.append("[SERVICES]")
        for sid in job.get("services", []):
            sinfo = service_map.get(sid, {})
            sname = sinfo.get("name", sid)
            sprice = float(sinfo.get("price", 0.0))
            lines.append(f"  {sname:<34} {sprice:>12,.2f}")

        job_parts = job.get("parts_used", [])
        if job_parts:
            lines.append("[PARTS REPLACED]")
            for jp in job_parts:
                pid = jp.get("part_id")
                qty = int(jp.get("quantity_used", 0))
                pinfo = parts_map.get(pid, {})
                pname = pinfo.get("name", pid)
                uprice = float(pinfo.get("unit_price", 0.0))
                sub = qty * uprice
                lines.append(f"  {pname} x{qty:<26} {sub:>12,.2f}")

        total_bill = models.compute_job_total(job, all_services, all_parts)
        total_paid = models.compute_payments_total(target_job_id, all_payments)
        balance = models.compute_balance(job, all_services, all_parts, all_payments)

        lines.append("-" * 55)
        lines.append(f"TOTAL BILL:                            PHP {total_bill:>10,.2f}")
        lines.append("-" * 55)
        lines.append("PAYMENT HISTORY:")
        if not job_payments:
            lines.append("  (No payments recorded yet)")
        else:
            for p in job_payments:
                p_id = p.get("payment_id")
                p_amt = float(p.get("amount", 0.0))
                p_m = p.get("method")
                p_d = p.get("date")
                lines.append(f"  [{p_d}] {p_id} ({p_m}): PHP {p_amt:,.2f}")

        lines.append("-" * 55)
        lines.append(f"TOTAL AMOUNT PAID:                     PHP {total_paid:>10,.2f}")
        lines.append(f"REMAINING BALANCE:                     PHP {balance:>10,.2f}")
        status_note = "FULLY PAID" if balance <= 0.0 else "BALANCE PENDING"
        lines.append(f"PAYMENT STATUS:                        {status_note}")
        lines.append("=" * 55)
        lines.append("          Thank you for choosing our service!          ")
        lines.append("=" * 55)

        full_content = "\n".join(lines)
        text_widget.insert(tk.END, full_content)
        text_widget.configure(state="disabled")

        btn_box = ttk.Frame(receipt_win, style="Surface.TFrame", padding=(20, 0, 20, 16))
        btn_box.pack(fill="x")

        def export_receipt_txt():
            try:
                export_dir = os.path.join(storage.BASE_DIR, "exports")
                if not os.path.exists(export_dir):
                    os.makedirs(export_dir)
                filepath = os.path.join(export_dir, f"receipt_{target_job_id}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full_content)
                messagebox.showinfo("Receipt Exported", f"Official receipt saved to:\n{filepath}", parent=receipt_win)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save receipt: {e}", parent=receipt_win)

        ttk.Button(btn_box, text="Close", style="Secondary.TButton", command=receipt_win.destroy).pack(side="left")
        ttk.Button(btn_box, text="Export as .txt", style="Primary.TButton", command=export_receipt_txt).pack(side="right")

    ttk.Button(btn_bar, text="Process Payment", style="Primary.TButton", command=open_payment_dialog).pack(side="left", padx=(0, 6))
    ttk.Button(btn_bar, text="View Official Receipt", style="Secondary.TButton", command=open_receipt_window).pack(side="left")

    refresh_table()
    return card
