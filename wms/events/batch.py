import frappe
from frappe.utils import getdate, date_diff, nowdate

def check_expiry_alert(doc, method):
    """
    Check batch expiry and create an alert if within threshold.
    """
    if not doc.expiry_date:
        return

    days_to_expiry = date_diff(getdate(doc.expiry_date), getdate(nowdate()))
    
    if days_to_expiry <= 30:
        # Create or update Batch Expiry Alert
        alert_name = frappe.db.get_value("Batch Expiry Alert", {"batch_id": doc.name}, "name")
        
        alert_data = {
            "doctype": "Batch Expiry Alert",
            "batch_id": doc.name,
            "item_code": doc.item,
            "expiry_date": doc.expiry_date,
            "days_to_expiry": days_to_expiry,
            "alert_level": get_alert_level(days_to_expiry)
        }

        if alert_name:
            alert = frappe.get_doc("Batch Expiry Alert", alert_name)
            alert.update(alert_data)
            alert.save()
        else:
            frappe.get_doc(alert_data).insert()

def get_alert_level(days):
    if days <= 0: return "Expired"
    if days <= 7: return "Red"
    if days <= 30: return "Orange"
    if days <= 90: return "Yellow"
    return "Green"
