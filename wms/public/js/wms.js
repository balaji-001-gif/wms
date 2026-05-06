/* WMS – Global JS utilities
 * Loaded via app_include_js in hooks.py
 * Compatible with Frappe v15 (ES2020+, no jQuery dependency required)
 */

frappe.provide("wms");

// ------------------------------------------------------------------
// Barcode scan handler – attach to any field with data-wms-barcode
// ------------------------------------------------------------------
wms.attach_barcode_scanner = function (frm, fieldname, callback) {
    const input = frm.get_field(fieldname).$input;
    if (!input) return;
    input.on("change", function () {
        const val = input.val().trim();
        if (val.length >= 6) {
            callback(val);
        }
    });
};

// ------------------------------------------------------------------
// Pick List WMS form helpers
// ------------------------------------------------------------------
frappe.ui.form.on("Pick List WMS", {
    refresh(frm) {
        if (frm.doc.status === "Draft" || frm.doc.status === "Assigned") {
            frm.add_custom_button(__("Start Picking"), () => {
                frappe.call({
                    method: "start_picking",
                    doc: frm.doc,
                    callback(r) {
                        if (r.message === "Started") {
                            frappe.show_alert({ message: "Picking started!", indicator: "green" });
                            frm.reload_doc();
                        }
                    },
                });
            }, __("Actions"));
        }

        if (frm.doc.status === "Picked" || frm.doc.status === "Short Pick") {
            frm.add_custom_button(__("Create Delivery Note"), () => {
                frappe.call({
                    method: "create_delivery_note",
                    doc: frm.doc,
                    callback(r) {
                        if (r.message) {
                            frappe.set_route("Form", "Delivery Note", r.message);
                        }
                    },
                });
            }, __("Actions"));
        }
    },

    pick_type(frm) {
        if (frm.doc.pick_type === "Batch Pick" || frm.doc.pick_type === "Wave Pick") {
            frappe.msgprint({
                title: __("Batch/Wave Picking"),
                message: __("Add multiple orders to the items table. The system will sort pick lines by zone automatically."),
                indicator: "blue",
            });
        }
    },
});

// ------------------------------------------------------------------
// Inbound Shipment form helpers
// ------------------------------------------------------------------
frappe.ui.form.on("Inbound Shipment", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.qc_required && frm.doc.status === "Received") {
            frm.add_custom_button(__("Mark QC Complete"), () => {
                frappe.call({
                    method: "mark_qc_complete",
                    doc: frm.doc,
                    callback() { frm.reload_doc(); },
                });
            }, __("QC"));
        }

        if (frm.doc.status === "Putaway Pending") {
            frm.set_intro(__("Putaway pending. Assign items to zones using the Putaway Plan table."), "orange");
        }
    },

    purchase_order(frm) {
        if (frm.doc.purchase_order) {
            frappe.call({
                method: "frappe.client.get",
                args: { doctype: "Purchase Order", name: frm.doc.purchase_order },
                callback(r) {
                    if (r.message) {
                        frm.set_value("supplier", r.message.supplier);
                        frm.clear_table("items");
                        r.message.items.forEach(item => {
                            frm.add_child("items", {
                                item_code: item.item_code,
                                item_name: item.item_name,
                                ordered_qty: item.qty,
                                uom: item.uom,
                            });
                        });
                        frm.refresh_field("items");
                    }
                },
            });
        }
    },
});

// ------------------------------------------------------------------
// Outbound Shipment
// ------------------------------------------------------------------
frappe.ui.form.on("Outbound Shipment", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === "Packing") {
            frm.add_custom_button(__("Manifest & Dispatch"), () => {
                frappe.prompt(
                    [
                        { label: "AWB / Tracking Number", fieldname: "tracking_number", fieldtype: "Data", reqd: 1 },
                        { label: "Carrier", fieldname: "carrier", fieldtype: "Link", options: "Supplier" },
                    ],
                    (values) => {
                        frappe.call({
                            method: "manifest_and_dispatch",
                            doc: frm.doc,
                            args: values,
                            callback() { frm.reload_doc(); },
                        });
                    },
                    __("Manifest Shipment"),
                    __("Confirm")
                );
            }, __("Actions"));
        }

        if (frm.doc.status === "Manifested") {
            frm.add_custom_button(__("Mark Dispatched"), () => {
                frappe.call({
                    method: "mark_dispatched",
                    doc: frm.doc,
                    callback() { frm.reload_doc(); },
                });
            }, __("Actions"));
        }
    },
});

// ------------------------------------------------------------------
// Cycle Count Entry
// ------------------------------------------------------------------
frappe.ui.form.on("Cycle Count Entry", {
    refresh(frm) {
        frm.add_custom_button(__("Populate System Qty"), () => {
            frappe.call({
                method: "populate_system_qty",
                doc: frm.doc,
                callback() { frm.reload_doc(); },
            });
        });

        if (frm.doc.status === "Pending Review") {
            frm.add_custom_button(__("Create Stock Reconciliation"), () => {
                frappe.confirm(
                    __("This will submit a Stock Reconciliation for all variance lines. Continue?"),
                    () => {
                        frappe.call({
                            method: "create_stock_reconciliation",
                            doc: frm.doc,
                            callback(r) {
                                if (r.message) {
                                    frappe.set_route("Form", "Stock Reconciliation", r.message);
                                }
                            },
                        });
                    }
                );
            }, __("Actions"));
        }
    },
});
