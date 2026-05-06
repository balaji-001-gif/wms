import frappe
from frappe.utils import today


def generate_daily_count_plan():
    """
    Runs at 2 AM daily. Generates a Cycle Count Entry for A-class items
    and rotates B/C-class on a weekly/monthly schedule.
    """
    warehouses = frappe.get_all("Warehouse", filters={"is_group": 0}, pluck="name")

    for warehouse in warehouses:
        # A-class: always count daily
        _create_count(warehouse, "ABC A-Class")

        # B-class: count on Mondays
        import datetime
        if datetime.date.today().weekday() == 0:
            _create_count(warehouse, "ABC B-Class")

        # C-class: count on 1st of month
        if datetime.date.today().day == 1:
            _create_count(warehouse, "ABC C-Class")

    frappe.db.commit()


def _create_count(warehouse, count_type):
    items = _get_items_for_count(warehouse, count_type)
    if not items:
        return

    cc = frappe.new_doc("Cycle Count Entry")
    cc.posting_date = today()
    cc.warehouse = warehouse
    cc.count_type = count_type

    for item_code in items:
        cc.append("items", {"item_code": item_code})

    cc.flags.ignore_permissions = True
    cc.insert()
    frappe.logger().info(f"WMS Cycle Count created: {cc.name} for {warehouse}")


def _get_items_for_count(warehouse, count_type):
    abc_map = {"ABC A-Class": "A", "ABC B-Class": "B", "ABC C-Class": "C"}
    abc = abc_map.get(count_type)
    if not abc:
        return []

    return frappe.db.sql_list(
        """
        SELECT DISTINCT sle.item_code
        FROM `tabStock Ledger Entry` sle
        JOIN `tabItem` i ON i.name = sle.item_code
        WHERE sle.warehouse = %s
          AND sle.is_cancelled = 0
          AND i.abc_classification = %s
        """,
        (warehouse, abc),
    )
