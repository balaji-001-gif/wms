import frappe

def on_purchase_receipt_submit(doc, method):
    """
    Triggered when a Purchase Receipt is submitted.
    Updates the related Inbound Shipment status.
    """
    # Find Inbound Shipment linked to this Purchase Receipt (via custom field or PO)
    inbound_shipment = frappe.db.get_value("Inbound Shipment", 
        {"purchase_order": doc.get("purchase_order"), "status": ["!=", "Completed"]}, 
        "name"
    )

    if inbound_shipment:
        is_doc = frappe.get_doc("Inbound Shipment", inbound_shipment)
        is_doc.db_set("linked_purchase_receipt", doc.name)
        
        # If putaway is done, mark as completed
        if is_doc.status == "Putaway Pending":
             is_doc.db_set("status", "Completed")
             frappe.msgprint(f"Inbound Shipment {inbound_shipment} marked as Completed.")
