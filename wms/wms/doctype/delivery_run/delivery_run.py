import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class DeliveryRun(Document):

    def validate(self):
        self.total_shipments = len(self.shipments)
        self.delivered_count = sum(1 for s in self.shipments if s.delivery_status == "Delivered")
        self.failed_count = sum(1 for s in self.shipments if s.delivery_status == "Failed")

    def on_submit(self):
        self.status = "Loading"
        self.save()
        self._link_shipments()

    def on_cancel(self):
        self.status = "Cancelled"
        self.save()

    def _link_shipments(self):
        for row in self.shipments:
            frappe.db.set_value("Outbound Shipment", row.outbound_shipment, "delivery_run", self.name)

    @frappe.whitelist()
    def start_run(self):
        self.db_set("status", "Out for Delivery")
        self.db_set("departure_time", now_datetime())

    @frappe.whitelist()
    def complete_run(self):
        self.db_set("status", "Completed")
        self.db_set("return_time", now_datetime())
        # Mark dispatched shipments as delivered
        for row in self.shipments:
            if row.delivery_status == "Delivered":
                frappe.db.set_value("Outbound Shipment", row.outbound_shipment, "status", "Delivered")
            elif row.delivery_status == "Failed":
                frappe.db.set_value("Outbound Shipment", row.outbound_shipment, "status", "RTO")
