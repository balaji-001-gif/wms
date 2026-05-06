import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CycleCountEntry(Document):

    def validate(self):
        self._compute_variance_summary()

    def on_submit(self):
        self.status = "Pending Review"
        self.save()

    def on_cancel(self):
        self.status = "Cancelled"
        self.save()

    # ------------------------------------------------------------------
    def _compute_variance_summary(self):
        self.total_lines = len(self.items)
        variance_lines = 0
        variance_value = 0.0

        for row in self.items:
            variance_qty = flt(row.counted_qty) - flt(row.system_qty)
            row.variance_qty = variance_qty
            if variance_qty != 0:
                variance_lines += 1
                rate = frappe.db.get_value("Item", row.item_code, "standard_rate") or 0
                variance_value += abs(variance_qty) * flt(rate)

        self.variance_lines = variance_lines
        self.variance_value = flt(variance_value, 2)

    @frappe.whitelist()
    def populate_system_qty(self):
        """Pull current stock qty for each item/zone from SLE."""
        for row in self.items:
            qty = frappe.db.sql(
                """
                SELECT qty_after_transaction FROM `tabStock Ledger Entry`
                WHERE item_code=%s AND warehouse=%s AND is_cancelled=0
                ORDER BY posting_date DESC, posting_time DESC LIMIT 1
                """,
                (row.item_code, self.warehouse),
            )
            row.system_qty = flt(qty[0][0] if qty else 0)
        self.save()
        frappe.msgprint("System quantities updated.", alert=True, indicator="blue")

    @frappe.whitelist()
    def create_stock_reconciliation(self):
        if self.status != "Pending Review":
            frappe.throw("Submit the count entry first.")
        if self.linked_stock_reconciliation:
            frappe.throw(f"Stock Reconciliation {self.linked_stock_reconciliation} already exists.")

        sr = frappe.new_doc("Stock Reconciliation")
        sr.company = frappe.defaults.get_user_default("company")
        sr.posting_date = self.posting_date
        sr.purpose = "Stock Reconciliation"

        for row in self.items:
            if flt(row.variance_qty) == 0:
                continue
            sr.append(
                "items",
                {
                    "item_code": row.item_code,
                    "warehouse": self.warehouse,
                    "qty": row.counted_qty,
                },
            )

        sr.flags.ignore_permissions = True
        sr.insert()
        sr.submit()
        self.db_set("linked_stock_reconciliation", sr.name)
        self.db_set("status", "Reconciled")
        frappe.msgprint(
            f"Stock Reconciliation <b>{sr.name}</b> submitted.", alert=True, indicator="green"
        )
        return sr.name
