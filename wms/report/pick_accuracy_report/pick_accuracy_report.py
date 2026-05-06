import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Pick List", "fieldname": "name", "fieldtype": "Link", "options": "Pick List WMS", "width": 150},
        {"label": "Picker", "fieldname": "picker", "fieldtype": "Link", "options": "User", "width": 160},
        {"label": "Pick Type", "fieldname": "pick_type", "fieldtype": "Data", "width": 120},
        {"label": "Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Total Lines", "fieldname": "total_lines", "fieldtype": "Int", "width": 100},
        {"label": "Picked Lines", "fieldname": "picked_lines", "fieldtype": "Int", "width": 100},
        {"label": "Short Lines", "fieldname": "short_lines", "fieldtype": "Int", "width": 100},
        {"label": "Accuracy %", "fieldname": "accuracy_pct", "fieldtype": "Percent", "width": 110},
        {"label": "Duration (mins)", "fieldname": "pick_duration_mins", "fieldtype": "Float", "width": 120},
        {"label": "Lines/Hour", "fieldname": "lines_per_hour", "fieldtype": "Float", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]


def get_data(filters):
    conditions = "WHERE docstatus = 1"
    values = {}

    if filters.get("picker"):
        conditions += " AND picker = %(picker)s"
        values["picker"] = filters["picker"]
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    rows = frappe.db.sql(
        f"""
        SELECT name, picker, pick_type, posting_date,
               total_lines, picked_lines, short_lines,
               pick_duration_mins, status
        FROM `tabPick List WMS`
        {conditions}
        ORDER BY posting_date DESC
        """,
        values,
        as_dict=True,
    )

    for row in rows:
        tl = row.total_lines or 0
        pl = row.picked_lines or 0
        row.accuracy_pct = flt(pl / tl * 100, 2) if tl else 0
        mins = flt(row.pick_duration_mins)
        row.lines_per_hour = flt(tl / (mins / 60), 2) if mins else 0

    return rows
