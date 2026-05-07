app_name = "wms"
app_title = "Warehouse Management System"
app_publisher = "WMS Team"
app_description = "End-to-end WMS for ERPNext v15+ inspired by Amazon, Flipkart, and Zepto workflows"
app_email = "support@wms-erpnext.com"
app_license = "MIT"
app_version = "1.0.0"

# ------------------------------------------------------------------
# Required Apps
# ------------------------------------------------------------------
required_apps = ["erpnext"]

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "wms"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "wms"]]},
    {"dt": "Workspace", "filters": [["module", "=", "wms"]]},
    {"dt": "Print Format", "filters": [["module", "=", "wms"]]},
    {"dt": "Role", "filters": [["name", "in", ["WMS Manager", "WMS Picker", "WMS Receiver", "WMS Packer"]]]},
    # Optional but recommended
    {"dt": "DocType", "filters": [["module", "=", "WMS"]]},
]

# ------------------------------------------------------------------
# Includes (Assets)
# ------------------------------------------------------------------
# Important: Use full /assets/ path for Frappe v15
app_include_js = "/assets/wms/js/wms.js"
# app_include_css = "/assets/wms/css/wms.css"      # Uncomment when you have CSS file

# ------------------------------------------------------------------
# Document Events
# ------------------------------------------------------------------
doc_events = {
    "Purchase Receipt": {
        "on_submit": "wms.wms.events.inbound.on_purchase_receipt_submit",
    },
    "Delivery Note": {
        "on_submit": "wms.wms.events.outbound.on_delivery_note_submit",
        "before_submit": "wms.wms.events.outbound.validate_pick_list_linked",
    },
    "Stock Entry": {
        "on_submit": "wms.wms.events.stock.on_stock_entry_submit",
    },
    "Batch": {
        "on_update": "wms.wms.events.batch.check_expiry_alert",
    },
}

# ------------------------------------------------------------------
# Scheduled Tasks
# ------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "wms.wms.tasks.batch_expiry.flag_expiring_batches",
        "wms.wms.tasks.replenishment.check_bin_levels",
    ],
    "hourly": [
        "wms.wms.tasks.slotting.auto_reslot_hot_items",
    ],
    "cron": {
        # Every 15 minutes – zone utilisation
        "*/15 * * * *": "wms.wms.tasks.zone_utilisation.refresh_zone_capacity",
        # Every night at 2 AM – cycle count
        "0 2 * * *": "wms.wms.tasks.cycle_count.generate_daily_count_plan",
    },
}

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
has_permission = {
    "Warehouse Zone": "wms.wms.permissions.warehouse_zone.has_permission",
    "Pick List WMS": "wms.wms.permissions.pick_list.has_permission",
}

# ------------------------------------------------------------------
# Jinja Helpers
# ------------------------------------------------------------------
jinja = {
    "methods": [
        "wms.wms.utils.jinja_helpers.get_zone_label",
        "wms.wms.utils.jinja_helpers.barcode_svg",
    ]
}

# ------------------------------------------------------------------
# After Migrate
# ------------------------------------------------------------------
after_migrate = [
    "wms.wms.setup.setup_roles",
    "wms.wms.setup.setup_default_warehouse_zones",
]

# ------------------------------------------------------------------
# Override Whitelisted Methods (if needed in future)
# ------------------------------------------------------------------
override_whitelisted_methods = {}
