app_name = "wms"
app_title = "Warehouse Management System"
app_publisher = "Your Company"
app_description = "End-to-end WMS for ERPNext v15+ inspired by Amazon, Flipkart, and Zepto workflows"
app_email = "dev@yourcompany.com"
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
app_include_css = "/assets/wms/css/wms.css"
app_include_js = "/assets/wms/js/wms.js"

# ------------------------------------------------------------------
# Document Events
# ------------------------------------------------------------------
doc_events = {
    "Purchase Receipt": {
        "on_submit": "wms.events.inbound.on_purchase_receipt_submit",
    },
    "Delivery Note": {
        "on_submit": "wms.events.outbound.on_delivery_note_submit",
        "before_submit": "wms.events.outbound.validate_pick_list_linked",
    },
    "Stock Entry": {
        "on_submit": "wms.events.stock.on_stock_entry_submit",
    },
    "Batch": {
        "on_update": "wms.events.batch.check_expiry_alert",
    },
}

# ------------------------------------------------------------------
# Scheduled Tasks
# ------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "wms.tasks.batch_expiry.flag_expiring_batches",
        "wms.tasks.replenishment.check_bin_levels",
    ],
    "hourly": [
        "wms.tasks.slotting.auto_reslot_hot_items",
    ],
    "cron": {
        # Every 15 min – real-time zone utilisation refresh
        "*/15 * * * *": [
            "wms.tasks.zone_utilisation.refresh_zone_capacity",
        ],
        # Every night at 2 AM – cycle count generation
        "0 2 * * *": [
            "wms.tasks.cycle_count.generate_daily_count_plan",
        ],
    },
}

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
has_permission = {
    "Warehouse Zone": "wms.permissions.warehouse_zone.has_permission",
    "Pick List WMS": "wms.permissions.pick_list.has_permission",
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
        "wms.utils.jinja_helpers.get_zone_label",
        "wms.utils.jinja_helpers.barcode_svg",
    ]
}

# ------------------------------------------------------------------
# After Migrate
# ------------------------------------------------------------------
after_migrate = [
    "wms.setup.setup_roles",
    "wms.setup.setup_default_warehouse_zones",
]
