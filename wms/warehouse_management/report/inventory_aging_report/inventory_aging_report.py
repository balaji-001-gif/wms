import frappe
from frappe.utils import flt, date_diff, today


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 160},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"label": "Batch No", "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 120},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 80},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 60},
        {"label": "Valuation Rate", "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 130},
        {"label": "Stock Value", "fieldname": "stock_value", "fieldtype": "Currency", "width": 130},
        {"label": "Last Movement Date", "fieldname": "last_movement", "fieldtype": "Date", "width": 140},
        {"label": "Aging (Days)", "fieldname": "aging_days", "fieldtype": "Int", "width": 110},
        {"label": "Aging Bucket", "fieldname": "aging_bucket", "fieldtype": "Data", "width": 120},
        {"label": "Expiry Date", "fieldname": "expiry_date", "fieldtype": "Date", "width": 110},
        {"label": "Days to Expiry", "fieldname": "days_to_expiry", "fieldtype": "Int", "width": 110},
    ]


def get_data(filters):
    warehouse_cond = ""
    values = {}
    if filters.get("warehouse"):
        warehouse_cond = "AND sle.warehouse = %(warehouse)s"
        values["warehouse"] = filters["warehouse"]

    item_group_cond = ""
    if filters.get("item_group"):
        item_group_cond = "AND i.item_group = %(item_group)s"
        values["item_group"] = filters["item_group"]

    raw = frappe.db.sql(
        f"""
        SELECT
            sle.item_code,
            i.item_name,
            sle.warehouse,
            sle.batch_no,
            SUM(sle.actual_qty) AS qty,
            i.stock_uom AS uom,
            AVG(sle.valuation_rate) AS valuation_rate,
            MAX(sle.posting_date) AS last_movement,
            b.expiry_date
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        LEFT JOIN `tabBatch` b ON b.name = sle.batch_no
        WHERE sle.is_cancelled = 0
          {warehouse_cond}
          {item_group_cond}
        GROUP BY sle.item_code, sle.warehouse, sle.batch_no
        HAVING qty > 0
        ORDER BY last_movement ASC
        """,
        values,
        as_dict=True,
    )

    result = []
    for row in raw:
        aging = date_diff(today(), str(row.last_movement)) if row.last_movement else 0
        row.aging_days = aging
        row.aging_bucket = _bucket(aging)
        row.stock_value = flt(row.qty) * flt(row.valuation_rate)
        if row.expiry_date:
            row.days_to_expiry = date_diff(str(row.expiry_date), today())
        else:
            row.days_to_expiry = None

        # Filter by aging if set
        if filters.get("min_aging_days") and aging < int(filters["min_aging_days"]):
            continue
        result.append(row)

    return result


def _bucket(days):
    if days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "31-60 days"
    elif days <= 90:
        return "61-90 days"
    elif days <= 180:
        return "91-180 days"
    else:
        return "180+ days"
