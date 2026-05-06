import frappe

def on_stock_entry_submit(doc, method):
    """
    Update Warehouse Zone utilization after Stock Entry.
    """
    affected_warehouses = set()
    for item in doc.items:
        if item.t_warehouse:
            affected_warehouses.add(item.t_warehouse)
        if item.s_warehouse:
            affected_warehouses.add(item.s_warehouse)

    for wh in affected_warehouses:
        zones = frappe.get_all("Warehouse Zone", filters={"warehouse": wh}, fields=["name"])
        for zone in zones:
            zone_doc = frappe.get_doc("Warehouse Zone", zone.name)
            zone_doc.run_method("validate") # This usually triggers capacity re-calc
            zone_doc.db_update()
