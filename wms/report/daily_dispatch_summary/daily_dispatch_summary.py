import frappe
from frappe.utils import flt, today


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 160},
        {"label": "Total Orders", "fieldname": "total_orders", "fieldtype": "Int", "width": 110},
        {"label": "Dispatched", "fieldname": "dispatched", "fieldtype": "Int", "width": 110},
        {"label": "RTO", "fieldname": "rto", "fieldtype": "Int", "width": 80},
        {"label": "Pending Pack", "fieldname": "pending_pack", "fieldtype": "Int", "width": 120},
        {"label": "Dispatch %", "fieldname": "dispatch_pct", "fieldtype": "Percent", "width": 110},
        {"label": "Avg Pack Time (mins)", "fieldname": "avg_pack_time", "fieldtype": "Float", "width": 150},
    ]


def get_data(filters):
    date = filters.get("date") or today()

    rows = frappe.db.sql(
        """
        SELECT
            IFNULL(channel, 'Unknown') AS channel,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN status IN ('Dispatched','Delivered') THEN 1 ELSE 0 END) AS dispatched,
            SUM(CASE WHEN status = 'RTO' THEN 1 ELSE 0 END) AS rto,
            SUM(CASE WHEN status IN ('Pick Pending','Packing','Manifested') THEN 1 ELSE 0 END) AS pending_pack
        FROM `tabOutbound Shipment`
        WHERE docstatus = 1 AND posting_date = %s
        GROUP BY channel
        ORDER BY total_orders DESC
        """,
        (date,),
        as_dict=True,
    )

    for row in rows:
        row.dispatch_pct = flt(row.dispatched / row.total_orders * 100, 2) if row.total_orders else 0
        row.avg_pack_time = 0  # Could be enriched from packing station logs

    return rows
