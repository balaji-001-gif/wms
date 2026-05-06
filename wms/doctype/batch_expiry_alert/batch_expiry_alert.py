import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today, getdate


class BatchExpiryAlert(Document):

    def before_save(self):
        self._compute_days_to_expiry()
        self._set_alert_level()

    # ------------------------------------------------------------------
    def _compute_days_to_expiry(self):
        if self.expiry_date:
            self.days_to_expiry = date_diff(self.expiry_date, today())

    def _set_alert_level(self):
        d = self.days_to_expiry or 0
        if d < 0:
            self.alert_level = "Expired"
        elif d <= 7:
            self.alert_level = "Red"
        elif d <= 30:
            self.alert_level = "Orange"
        elif d <= 90:
            self.alert_level = "Yellow"
        else:
            self.alert_level = "Green"
