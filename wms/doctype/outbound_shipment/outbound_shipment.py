import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class OutboundShipment(Document):

    def validate(self):
        self._validate_items()

    def on_submit(self):
        self.status = "Pick Pending"
        self.save()
        self._auto_create_pick_list()

    def on_cancel(self):
        self.status = "Cancelled"
        self.save()

    # ------------------------------------------------------------------
    def _validate_items(self):
        if not self.items:
            frappe.throw("At least one item is required.")

    def _auto_create_pick_list(self):
        pick = frappe.new_doc("Pick List WMS")
        pick.pick_type = "Single Order"
        pick.warehouse = self.warehouse
        pick.priority = "High" if self.channel in ("Zepto", "Blinkit", "Swiggy Instamart") else "Normal"
        for row in self.items:
            pick.append(
                "items",
                {
                    "item_code": row.item_code,
                    "qty": row.qty,
                    "warehouse": self.warehouse,
                    "source_outbound": self.name,
                },
            )
        pick.flags.ignore_permissions = True
        pick.insert()
        self.db_set("pick_list_wms", pick.name)
        self.db_set("status", "Pick Pending")
        frappe.msgprint(
            f"Pick List <b>{pick.name}</b> created.", alert=True, indicator="green"
        )

    @frappe.whitelist()
    def mark_packed(self):
        self.db_set("status", "Packing")
        self.db_set("packed_on", now_datetime())
        self.db_set("packed_by", frappe.session.user)

    @frappe.whitelist()
    def manifest_and_dispatch(self, tracking_number, carrier=None):
        self.db_set("tracking_number", tracking_number)
        if carrier:
            self.db_set("carrier", carrier)
        self.db_set("status", "Manifested")
        frappe.msgprint(f"Shipment manifested. AWB: {tracking_number}", alert=True, indicator="green")

    @frappe.whitelist()
    def mark_dispatched(self):
        if self.status != "Manifested":
            frappe.throw("Shipment must be manifested before dispatch.")
        self.db_set("status", "Dispatched")
