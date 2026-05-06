import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class InboundShipment(Document):

    def validate(self):
        self._validate_items()
        if self.putaway_strategy and self.putaway_strategy != "Manual":
            self._auto_generate_putaway_plan()

    def on_submit(self):
        self.status = "Received"
        self.actual_arrival = now_datetime()
        if not self.qc_required:
            self._trigger_putaway()
        self.save()

    def on_cancel(self):
        self.status = "Rejected"
        self.save()

    def _validate_items(self):
        for row in self.items:
            if flt(row.get("received_qty", 0)) < 0:
                frappe.throw(f"Row {row.idx}: Received Qty cannot be negative.")

    def _auto_generate_putaway_plan(self):
        self.putaway_details = []
        zones = frappe.get_all(
            "Warehouse Zone",
            filters={"warehouse": self.warehouse, "is_active": 1},
            fields=["name", "zone_code", "zone_type", "priority"],
            order_by="priority asc",
        )
        for item_row in self.items:
            remaining = flt(item_row.get("received_qty", 0))
            for zone in zones:
                if zone.zone_type not in ("Putaway", "Storage"):
                    continue
                if remaining <= 0:
                    break

    def _trigger_putaway(self):
        self.status = "Putaway Pending"

    @frappe.whitelist()
    def mark_qc_complete(self):
        if self.status != "Received":
            frappe.throw("QC can only be completed after receiving.")
        self.db_set("status", "Putaway Pending")
        frappe.msgprint("QC marked complete.", indicator="green", alert=True)
