import frappe

def has_permission(doc, ptype, user):
    """
    Control access to Warehouse Zones based on roles.
    """
    if "WMS Manager" in frappe.get_roles(user):
        return True
    
    # Receivers can only read zones
    if "WMS Receiver" in frappe.get_roles(user) and ptype == "read":
        return True
        
    return False
