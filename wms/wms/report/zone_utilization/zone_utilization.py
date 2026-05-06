import frappe
from frappe.utils import flt


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": "Zone Code", "fieldname": "zone_code", "fieldtype": "Link", "options": "Warehouse Zone", "width": 120},
        {"label": "Zone Name", "fieldname": "zone_name", "fieldtype": "Data", "width": 160},
        {"label": "Zone Type", "fieldname": "zone_type", "fieldtype": "Data", "width": 120},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"label": "Max Capacity (kg)", "fieldname": "max_capacity_kg", "fieldtype": "Float", "width": 140},
        {"label": "Utilisation %", "fieldname": "current_utilisation_pct", "fieldtype": "Percent", "width": 120},
        {"label": "Status", "fieldname": "utilisation_status", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = ""
    values = {}
    if filters.get("warehouse"):
        conditions = "WHERE warehouse = %(warehouse)s"
        values["warehouse"] = filters["warehouse"]

    rows = frappe.db.sql(
        f"""
        SELECT zone_code, zone_name, zone_type, warehouse,
               max_capacity_kg, current_utilisation_pct
        FROM `tabWarehouse Zone`
        {conditions}
        ORDER BY current_utilisation_pct DESC
        """,
        values,
        as_dict=True,
    )

    for row in rows:
        pct = flt(row.current_utilisation_pct)
        if pct >= 90:
            row.utilisation_status = "Critical"
        elif pct >= 70:
            row.utilisation_status = "High"
        elif pct >= 40:
            row.utilisation_status = "Normal"
        else:
            row.utilisation_status = "Low"

    return rows
