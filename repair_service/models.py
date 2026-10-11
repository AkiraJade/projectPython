# Model logic, ID generators, calculations, and status rules

from datetime import datetime

# Workflow statuses in standard sequence
STATUS_LIST = [
    "Pending Drop-off",
    "Received",
    "Diagnosing",
    "Waiting for Parts",
    "Under Repair",
    "Completed",
    "Released",
    "Cancelled"
]

# Statuses where the job is considered active (not finished or cancelled)
ACTIVE_STATUSES = [
    "Pending Drop-off",
    "Received",
    "Diagnosing",
    "Waiting for Parts",
    "Under Repair",
    "Completed"
]

# Valid status transitions to prevent invalid status jumps
VALID_TRANSITIONS = {
    "Pending Drop-off": ["Received", "Cancelled"],
    "Received": ["Diagnosing", "Waiting for Parts", "Under Repair", "Cancelled"],
    "Diagnosing": ["Waiting for Parts", "Under Repair", "Completed", "Cancelled"],
    "Waiting for Parts": ["Under Repair", "Diagnosing", "Completed", "Cancelled"],
    "Under Repair": ["Waiting for Parts", "Completed", "Cancelled"],
    "Completed": ["Under Repair", "Released", "Cancelled"],
    "Released": [],
    "Cancelled": []
}


def is_valid_transition(current_status, new_status):
    """Check if transitioning from current_status to new_status is allowed."""
    if current_status == new_status:
        return True
    allowed = VALID_TRANSITIONS.get(current_status, [])
    return new_status in allowed


def generate_id(prefix, records, id_key):
    """
    Generate the next ID with a prefix and zero-padded 3-digit number.
    Example: prefix 'CUST-', records with 'CUST-001' -> returns 'CUST-002'.
    """
    max_num = 0
    for item in records:
        val = item.get(id_key, "")
        if val.startswith(prefix):
            suffix = val[len(prefix):]
            if suffix.isdigit():
                num = int(suffix)
                if num > max_num:
                    max_num = num
    next_num = max_num + 1
    return f"{prefix}{next_num:03d}"


def create_status_log(job_id, status):
    """Create a timestamped record for a status change."""
    return {
        "job_id": job_id,
        "status": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def compute_services_total(service_ids, all_services):
    """Calculate the sum of prices for the list of service IDs attached to a job."""
    service_map = {s["service_id"]: float(s.get("price", 0.0)) for s in all_services}
    total = 0.0
    for sid in service_ids:
        if sid in service_map:
            total += service_map[sid]
    return total


def compute_parts_total(job_parts, all_parts):
    """Calculate the sum of parts used (quantity * unit price)."""
    parts_map = {p["part_id"]: float(p.get("unit_price", 0.0)) for p in all_parts}
    total = 0.0
    for jp in job_parts:
        pid = jp.get("part_id")
        qty = int(jp.get("quantity_used", 0))
        if pid in parts_map:
            total += parts_map[pid] * qty
    return total


def compute_job_total(job, all_services, all_parts):
    """Calculate overall total bill for a job order."""
    services_sum = compute_services_total(job.get("services", []), all_services)
    parts_sum = compute_parts_total(job.get("parts_used", []), all_parts)
    return round(services_sum + parts_sum, 2)


def compute_payments_total(job_id, all_payments):
    """Sum all payments made towards a specific job order."""
    total = 0.0
    for p in all_payments:
        if p.get("job_id") == job_id:
            try:
                total += float(p.get("amount", 0.0))
            except (ValueError, TypeError):
                pass
    return round(total, 2)


def compute_balance(job, all_services, all_parts, all_payments):
    """Calculate remaining unpaid balance for a job order."""
    total_bill = compute_job_total(job, all_services, all_parts)
    total_paid = compute_payments_total(job.get("job_id"), all_payments)
    balance = total_bill - total_paid
    return round(max(0.0, balance), 2)


def is_job_paid(job, all_services, all_parts, all_payments):
    """Check if the job has 0 remaining balance."""
    return compute_balance(job, all_services, all_parts, all_payments) <= 0.0
