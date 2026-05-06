import frappe
from frappe.utils import today, date_diff, flt


def flag_expiring_batches():
    """
    Runs daily. Creates or updates Batch Expiry Alert records
    for any batch nearing expiry within 180 days.
    """
    batches = frappe.db.sql(
        """
        SELECT
            b.name AS batch_no,
            b.item AS item_code,
            b.expiry_date,
            SUM(sle.actual_qty) AS available_qty,
            sle.warehouse
        FROM `tabBatch` b
        JOIN `tabStock Ledger Entry` sle ON sle.batch_no = b.name
        WHERE b.expiry_date IS NOT NULL
          AND b.expiry_date >= CURDATE()
          AND sle.is_cancelled = 0
        GROUP BY b.name, sle.warehouse
        HAVING available_qty > 0
        """,
        as_dict=True,
    )

    for row in batches:
        days = date_diff(str(row.expiry_date), today())
        if days > 180:
            continue  # Not worth alerting yet

        existing = frappe.db.get_value(
            "Batch Expiry Alert",
            {"batch_no": row.batch_no, "warehouse": row.warehouse},
            "name",
        )

        if existing:
            frappe.db.set_value(
                "Batch Expiry Alert",
                existing,
                {
                    "days_to_expiry": days,
                    "available_qty": flt(row.available_qty),
                },
            )
        else:
            doc = frappe.new_doc("Batch Expiry Alert")
            doc.item_code = row.item_code
            doc.batch_no = row.batch_no
            doc.warehouse = row.warehouse
            doc.expiry_date = row.expiry_date
            doc.days_to_expiry = days
            doc.available_qty = flt(row.available_qty)
            doc.flags.ignore_permissions = True
            doc.insert()

    frappe.db.commit()
    frappe.logger().info(f"WMS batch expiry scan complete. {len(batches)} batches checked.")
