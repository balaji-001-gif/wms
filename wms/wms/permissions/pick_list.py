import frappe

def has_permission(doc, ptype, user):
    """
    Pickers can only access Pick Lists assigned to them.
    Managers have full access.
    """
    if "WMS Manager" in frappe.get_roles(user):
        return True

    if "WMS Picker" in frappe.get_roles(user):
        if ptype == "read":
            return True
        if ptype == "write" and doc.picker == user:
            return True

    return False
