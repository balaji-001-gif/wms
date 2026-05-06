app_name = "wms"
app_title = "Warehouse Management System"
app_publisher = "WMS Team"
app_description = "End-to-end WMS for ERPNext v15+ inspired by Amazon, Flipkart, and Zepto workflows"
app_email = "support@wms-erpnext.com"
app_license = "MIT"
app_version = "1.0.0"

# ------------------------------------------------------------------
# Required apps
# ------------------------------------------------------------------
required_apps = ["erpnext"]

# ------------------------------------------------------------------
# Fixtures – exported via bench export-fixtures
# ------------------------------------------------------------------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "WMS"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "WMS"]]},
    {"dt": "Workspace", "filters": [["module", "=", "WMS"]]},
    {"dt": "Print Format", "filters": [["module", "=", "WMS"]]},
    {"dt": "Role", "filters": [["name", "in", ["WMS Manager", "WMS Picker", "WMS Receiver", "WMS Packer"]]]},
]

# ------------------------------------------------------------------
# Includes
# ------------------------------------------------------------------
# app_include_css = "wms.css"
# app_include_js = "wms.js"

# ------------------------------------------------------------------
# Document Events
# ------------------------------------------------------------------
doc_events = {
    "Purchase Receipt": {
        "on_submit": "wms.warehouse_management.events.inbound.on_purchase_receipt_submit",
    },
    "Delivery Note": {
        "on_submit": "wms.warehouse_management.events.outbound.on_delivery_note_submit",
        "before_submit": "wms.warehouse_management.events.outbound.validate_pick_list_linked",
    },
    "Stock Entry": {
        "on_submit": "wms.warehouse_management.events.stock.on_stock_entry_submit",
    },
    "Batch": {
        "on_update": "wms.warehouse_management.events.batch.check_expiry_alert",
    },
}

# ------------------------------------------------------------------
# Scheduled Tasks
# ------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "wms.warehouse_management.tasks.batch_expiry.flag_expiring_batches",
        "wms.warehouse_management.tasks.replenishment.check_bin_levels",
    ],
    "hourly": [
        "wms.warehouse_management.tasks.slotting.auto_reslot_hot_items",
    ],
    "cron": {
        # Every 15 min – real-time zone utilisation refresh
        "*/15 * * * *": [
            "wms.warehouse_management.tasks.zone_utilisation.refresh_zone_capacity",
        ],
        # Every night at 2 AM – cycle count generation
        "0 2 * * *": [
            "wms.warehouse_management.tasks.cycle_count.generate_daily_count_plan",
        ],
    },
}

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
has_permission = {
    "Warehouse Zone": "wms.warehouse_management.permissions.warehouse_zone.has_permission",
    "Pick List WMS": "wms.warehouse_management.permissions.pick_list.has_permission",
}

# ------------------------------------------------------------------
# Override Whitelisted Methods
# ------------------------------------------------------------------
override_whitelisted_methods = {}

# ------------------------------------------------------------------
# Jinja
# ------------------------------------------------------------------
jinja = {
    "methods": [
        "wms.warehouse_management.utils.jinja_helpers.get_zone_label",
        "wms.warehouse_management.utils.jinja_helpers.barcode_svg",
    ]
}

# ------------------------------------------------------------------
# After Migrate
# ------------------------------------------------------------------
# after_migrate = [
#     "wms.warehouse_management.setup.setup_roles",
#     "wms.warehouse_management.setup.setup_default_warehouse_zones",
# ]
