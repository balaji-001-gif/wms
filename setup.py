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

    default_warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    if not default_warehouse:
        # Fallback to any warehouse if default is not set
        default_warehouse = frappe.db.get_value("Warehouse", {"is_group": 0}, "name")

    if not default_warehouse:
        return

    zones = [
        {"zone_code": "REC-01", "zone_name": "Receiving Dock", "zone_type": "Receiving", "priority": 1},
        {"zone_code": "STG-A", "zone_name": "Storage Area A", "zone_type": "Storage", "priority": 10},
        {"zone_code": "PCK-01", "zone_name": "Picking Zone 01", "zone_type": "Picking", "priority": 5},
        {"zone_code": "PAK-01", "zone_name": "Packing Station 01", "zone_type": "Packing", "priority": 2},
        {"zone_code": "DSP-01", "zone_name": "Dispatch Area", "zone_type": "Dispatch", "priority": 1},
        {"zone_code": "CLD-01", "zone_name": "Cold Storage", "zone_type": "Cold", "priority": 10, "temperature_zone": "Frozen"},
        {"zone_code": "RTN-01", "zone_name": "Returns Processing", "zone_type": "Return", "priority": 20},
    ]

    for zone in zones:
        doc = frappe.get_doc({
            "doctype": "Warehouse Zone",
            "warehouse": default_warehouse,
            **zone
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
