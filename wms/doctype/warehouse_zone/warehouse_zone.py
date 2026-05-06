import frappe
from frappe.model.document import Document
from frappe.utils import flt


class WarehouseZone(Document):

    def validate(self):
        self._validate_bin_codes_unique()
        self._compute_utilisation()

    def _validate_bin_codes_unique(self):
        codes = [row.bin_code for row in self.bins_table]
        if len(codes) != len(set(codes)):
            frappe.throw("Duplicate bin codes found in this zone.")

    def _compute_utilisation(self):
        if not self.max_capacity_kg:
            return
        total_weight = frappe.db.sql(
            """
            SELECT SUM(i.weight_per_unit * sle.qty_after_transaction)
            FROM `tabStock Ledger Entry` sle
            JOIN `tabItem` i ON i.name = sle.item_code
            WHERE sle.warehouse = %s
              AND sle.is_cancelled = 0
            """,
            (self.warehouse,),
        )
        total_kg = flt(total_weight[0][0] if total_weight else 0)
        self.current_utilisation_pct = min(
            flt(total_kg / self.max_capacity_kg * 100, 2), 100
        )

    @frappe.whitelist()
    def get_available_bins(self, item_code=None):
        """Return bins in this zone with available capacity."""
        bins = []
        for b in self.bins_table:
            if b.is_locked:
                continue
            bins.append(
                {
                    "bin_code": b.bin_code,
                    "bin_type": b.bin_type,
                    "max_qty": b.max_qty,
                    "current_qty": b.current_qty,
                    "available_qty": flt(b.max_qty) - flt(b.current_qty),
                }
            )
        return bins
