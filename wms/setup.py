import frappe


def setup_roles():
    roles = ["WMS Manager", "WMS Picker", "WMS Receiver", "WMS Packer"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert()
    frappe.db.commit()


def setup_default_warehouse_zones():
    # Skip if table doesn't exist yet
    if not frappe.db.table_exists("Warehouse Zone"):
        return
    if frappe.db.count("Warehouse Zone") > 0:
        return
    frappe.db.commit()
