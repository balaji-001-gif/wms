import frappe
from frappe.utils import add_days, nowdate
import random

def create_demo_data():
    print("Starting Demo Data Generation...")
    
    # 1. Ensure a Warehouse exists
    warehouse = "Demo Warehouse - W"
    if not frappe.db.exists("Warehouse", warehouse):
        frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Demo Warehouse",
            "is_group": 0
        }).insert(ignore_permissions=True)
    
    # 2. Create Warehouse Zones
    zones = [
        {"code": "Z-REC-01", "name": "Receiving Zone 1", "type": "Receiving"},
        {"code": "Z-STO-01", "name": "Bulk Storage A1", "type": "Storage"},
        {"code": "Z-PIC-01", "name": "Active Picking Zone", "type": "Picking"},
        {"code": "Z-DIS-01", "name": "Dispatch Staging", "type": "Dispatch"},
        {"code": "Z-COL-01", "name": "Cold Storage Unit", "type": "Cold Storage"}
    ]
    
    for z in zones:
        if not frappe.db.exists("Warehouse Zone", z["code"]):
            frappe.get_doc({
                "doctype": "Warehouse Zone",
                "zone_code": z["code"],
                "zone_name": z["name"],
                "zone_type": z["type"],
                "warehouse": warehouse,
                "is_active": 1
            }).insert(ignore_permissions=True)
    
    # 3. Create Warehouse Zone Bins
    for i in range(1, 11):
        bin_id = f"BIN-{i:03}"
        if not frappe.db.exists("Warehouse Zone Bin", bin_id):
            frappe.get_doc({
                "doctype": "Warehouse Zone Bin",
                "bin_id": bin_id,
                "zone": "Z-STO-01",
                "warehouse": warehouse,
                "max_capacity_kg": 500,
                "is_active": 1
            }).insert(ignore_permissions=True)

    # 4. Create Sample Items
    items = []
    for i in range(1, 6):
        item_code = f"WMS-ITEM-{i:03}"
        items.append(item_code)
        if not frappe.db.exists("Item", item_code):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": item_code,
                "item_name": f"WMS Sample Product {i}",
                "item_group": "All Item Groups",
                "is_stock_item": 1,
                "opening_stock": 100,
                "valuation_rate": 10 * i,
                "stock_uom": "Nos"
            }).insert(ignore_permissions=True)

    # 5. Create Inbound Shipments (10 entries)
    for i in range(1, 11):
        doc = frappe.get_doc({
            "doctype": "Inbound Shipment",
            "vendor": "Sample Vendor",
            "expected_arrival": add_days(nowdate(), random.randint(1, 5)),
            "warehouse": warehouse,
            "status": "Draft",
            "items": [
                {
                    "item_code": random.choice(items),
                    "expected_qty": random.randint(50, 200),
                    "uom": "Nos"
                } for _ in range(random.randint(1, 3))
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created Inbound Shipment: {doc.name}")

    # 6. Create Outbound Shipments (10 entries)
    for i in range(1, 11):
        doc = frappe.get_doc({
            "doctype": "Outbound Shipment",
            "customer": "Sample Customer",
            "delivery_date": add_days(nowdate(), random.randint(2, 7)),
            "warehouse": warehouse,
            "status": "Draft",
            "items": [
                {
                    "item_code": random.choice(items),
                    "qty": random.randint(10, 50),
                    "uom": "Nos"
                } for _ in range(random.randint(1, 3))
            ]
        })
        doc.insert(ignore_permissions=True)
        print(f"Created Outbound Shipment: {doc.name}")

    # 7. Create Putaway Rules
    for item in items:
        if not frappe.db.exists("Putaway Rule", {"item_code": item}):
            frappe.get_doc({
                "doctype": "Putaway Rule",
                "item_code": item,
                "preferred_zone": "Z-STO-01",
                "warehouse": warehouse,
                "priority": 1
            }).insert(ignore_permissions=True)

    frappe.db.commit()
    print("Demo Data Generation Complete!")

if __name__ == "__main__":
    create_demo_data()
