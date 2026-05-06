import frappe
from frappe.tests.utils import FrappeTestCase

class TestPickListWMS(FrappeTestCase):
    def test_pick_list_sorting(self):
        """Test if pick lines are sorted by zone and bin."""
        doc = frappe.get_doc({
            "doctype": "Pick List WMS",
            "pick_type": "Single Order",
            "items": [
                {"item_code": "Item 1", "qty": 1, "zone": "Zone B", "bin_code": "Bin 1"},
                {"item_code": "Item 2", "qty": 1, "zone": "Zone A", "bin_code": "Bin 2"},
                {"item_code": "Item 3", "qty": 1, "zone": "Zone A", "bin_code": "Bin 1"},
            ]
        })
        doc.validate()
        
        self.assertEqual(doc.items[0].zone, "Zone A")
        self.assertEqual(doc.items[0].bin_code, "Bin 1")
        self.assertEqual(doc.items[1].bin_code, "Bin 2")
        self.assertEqual(doc.items[2].zone, "Zone B")

    def test_status_transitions(self):
        """Test picking status transitions."""
        doc = frappe.get_doc({
            "doctype": "Pick List WMS",
            "pick_type": "Single Order",
            "items": [{"item_code": "Item 1", "qty": 1, "zone": "Zone A", "bin_code": "Bin 1"}]
        }).insert()
        
        doc.start_picking()
        self.assertEqual(doc.status, "In Progress")
        self.assertIsNotNone(doc.start_time)
        
        doc.confirm_pick_line("Item 1", "Bin 1", 1)
        self.assertEqual(doc.status, "Picked")
        self.assertIsNotNone(doc.end_time)
