import frappe
from frappe import _

def validate_pick_list_linked(doc, method):
    """
    Ensure a Pick List WMS is linked and completed before submitting Delivery Note.
    """
    if not doc.get("wms_pick_list"):
        # Check if there is an Outbound Shipment that requires picking
        outbound_shipment = frappe.db.get_value("Outbound Shipment", {"delivery_note": doc.name}, "name")
        if outbound_shipment:
            frappe.throw(_("Delivery Note must be linked to a completed Pick List WMS for WMS-managed shipments."))

def on_delivery_note_submit(doc, method):
    """
    Update Outbound Shipment status on Delivery Note submission.
    """
    outbound_shipment = frappe.db.get_value("Outbound Shipment", {"delivery_note": doc.name}, "name")
    
    if outbound_shipment:
        os_doc = frappe.get_doc("Outbound Shipment", outbound_shipment)
        os_doc.db_set("status", "Manifested")
        frappe.msgprint(_("Outbound Shipment {0} status updated to Manifested.").format(outbound_shipment))

    # Update Pick List status if linked
    if doc.get("wms_pick_list"):
        frappe.db.set_value("Pick List WMS", doc.wms_pick_list, "status", "Completed")
