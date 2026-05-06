import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt, time_diff_in_seconds


class PickListWMS(Document):

    def validate(self):
        self.total_lines = len(self.items)
        self.picked_lines = sum(1 for r in self.items if flt(r.picked_qty) >= flt(r.qty))
        self.short_lines = sum(
            1 for r in self.items if 0 < flt(r.picked_qty) < flt(r.qty)
        )
        self._sort_items_by_zone()

    def on_submit(self):
        if self.status == "Draft":
            self.status = "Assigned"
        self.save()
        self._notify_picker()

    def on_cancel(self):
        self.status = "Cancelled"
        self.save()

    # ------------------------------------------------------------------
    def _sort_items_by_zone(self):
        """Sort pick lines by zone then bin for optimal travel path."""
        self.items.sort(key=lambda r: (r.get("zone") or "", r.get("bin_code") or ""))
        for idx, row in enumerate(self.items, start=1):
            row.idx = idx

    def _notify_picker(self):
        if not self.picker:
            return
        frappe.sendmail(
            recipients=[self.picker],
            subject=f"[WMS] Pick List {self.name} Assigned",
            message=f"You have been assigned pick list <b>{self.name}</b>.<br>"
                    f"Priority: {self.priority} | Lines: {self.total_lines}<br>"
                    f"SLA Deadline: {self.sla_deadline or 'Not set'}",
        )

    @frappe.whitelist()
    def start_picking(self):
        if self.status not in ("Draft", "Assigned"):
            frappe.throw("Can only start picking from Draft or Assigned state.")
        self.db_set("status", "In Progress")
        self.db_set("start_time", now_datetime())
        return "Started"

    @frappe.whitelist()
    def confirm_pick_line(self, item_code, bin_code, picked_qty):
        for row in self.items:
            if row.item_code == item_code and row.bin_code == bin_code:
                row.picked_qty = flt(picked_qty)
                row.is_confirmed = 1
                break
        self.save()
        return self._check_completion()

    def _check_completion(self):
        all_confirmed = all(r.is_confirmed for r in self.items)
        if all_confirmed:
            self.end_time = now_datetime()
            if self.start_time:
                self.pick_duration_mins = flt(
                    time_diff_in_seconds(self.end_time, self.start_time) / 60, 2
                )
            has_shorts = any(flt(r.picked_qty) < flt(r.qty) for r in self.items)
            self.status = "Short Pick" if has_shorts else "Picked"
            self.save()
            return self.status
        return "In Progress"

    @frappe.whitelist()
    def create_delivery_note(self):
        """Create Delivery Note from confirmed pick."""
        if self.status not in ("Picked", "Short Pick"):
            frappe.throw("Pick must be completed before creating Delivery Note.")
        if self.linked_delivery_note:
            frappe.throw(f"Delivery Note {self.linked_delivery_note} already exists.")

        dn = frappe.new_doc("Delivery Note")
        dn.company = frappe.defaults.get_user_default("company")
        dn.posting_date = frappe.utils.today()
        dn.wms_pick_list = self.name

        for row in self.items:
            if flt(row.picked_qty) <= 0:
                continue
            dn.append(
                "items",
                {
                    "item_code": row.item_code,
                    "qty": row.picked_qty,
                    "warehouse": row.warehouse or self.warehouse,
                },
            )

        dn.flags.ignore_permissions = True
        dn.insert()
        self.db_set("linked_delivery_note", dn.name)
        frappe.msgprint(
            f"Delivery Note <b>{dn.name}</b> created.", alert=True, indicator="green"
        )
        return dn.name
