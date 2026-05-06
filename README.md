# WMS – Warehouse Management System for ERPNext v15+

> **A production-grade Frappe/ERPNext v15 custom app** modelled after Amazon Fulfillment Center operations, Flipkart's wave-pick architecture, and Zepto's quick-commerce last-mile model.

---

## Table of Contents

1. [Overview](#overview)
2. [Industry Benchmarking](#industry-benchmarking)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [DocTypes](#doctypes)
6. [Reports](#reports)
7. [Workspace](#workspace)
8. [Notifications](#notifications)
9. [Scheduled Tasks](#scheduled-tasks)
10. [Roles & Permissions](#roles--permissions)
11. [Installation](#installation)
12. [Configuration](#configuration)
13. [Extending the App](#extending-the-app)
14. [FAQ](#faq)

---

## Overview

This app adds a dedicated **Warehouse Management layer on top of ERPNext v15** — covering:

| Domain | Coverage |
|---|---|
| **Inbound** | Gate receive → QC → Auto/Manual Putaway → PR creation |
| **Storage** | Zone + Bin management, capacity tracking, FEFO batch alerting |
| **Outbound** | Order release → Wave/Batch pick → Packing station → Manifest → Dispatch |
| **Last Mile** | Delivery Run routing, rider assignment, RTO handling |
| **Inventory** | ABC cycle counting, variance capture, automatic Stock Reconciliation |
| **Analytics** | Pick accuracy, aging, zone utilisation, dispatch throughput |

All documents are native Frappe DocTypes — fully visible in list views, form views, print formats, and the permission system. No external database or microservice required.

---

## Industry Benchmarking

### Amazon Fulfillment Center (FC) Model
| FC Process | WMS Equivalent |
|---|---|
| Receive → Stow | Inbound Shipment → Putaway Plan |
| Pick cart wave | Pick List WMS (Wave Pick type) |
| Pack station | Packing Station DocType + Outbound Shipment |
| Ship → Track | Outbound Shipment (Manifested → Dispatched) |
| Cycle count | Cycle Count Entry (ABC rotation) |

### Flipkart Warehouse Model
| Flipkart Process | WMS Equivalent |
|---|---|
| GRN / Inward | Inbound Shipment → Purchase Receipt |
| Bin slotting | Warehouse Zone + Slotting Config |
| Batch picking | Pick List WMS (Batch Pick type) |
| QC check | Inbound Shipment QC section |
| Dispatch SLA | Outbound Shipment SLA deadline |

### Zepto Quick Commerce Model
| Zepto Process | WMS Equivalent |
|---|---|
| Dark store receive | Inbound Shipment (fast receive, no QC) |
| 10-min pick | Pick List WMS (priority=Urgent, Cluster Pick) |
| Batch expiry (FEFO) | Batch Expiry Alert + scheduler |
| Rider dispatch | Delivery Run (vehicle/rider assignment) |
| RTO handling | Outbound Shipment status = RTO |

---

## Architecture

```
ERPNext v15 Core
└── WMS App (Custom Frappe App)
    ├── DocTypes (models/controllers)
    │   ├── Warehouse Zone          ← Physical zone/bin map
    │   ├── Inbound Shipment        ← GRN + putaway trigger
    │   ├── Pick List WMS           ← Wave/batch/single picking
    │   ├── Outbound Shipment       ← Pack → Manifest → Dispatch
    │   ├── Delivery Run            ← Last-mile route plan
    │   ├── Cycle Count Entry       ← Physical inventory audit
    │   ├── Batch Expiry Alert      ← FEFO monitoring
    │   ├── Putaway Rule            ← Configurable putaway logic
    │   ├── Slotting Config         ← Hot-slot vs cold-slot config
    │   ├── Kitting Order           ← Bundle/kit assembly
    │   └── Packing Station         ← Workstation metadata
    ├── Reports (Script Reports)
    │   ├── Inventory Aging Report
    │   ├── Pick Accuracy Report
    │   ├── Daily Dispatch Summary
    │   ├── Zone Utilization
    │   ├── Inbound vs Outbound
    │   └── Slotting Efficiency
    ├── Workspace                   ← WMS dashboard tab
    ├── Notifications               ← Email/in-app alerts
    ├── Scheduled Tasks             ← Batch expiry, cycle count gen
    ├── Fixtures                    ← Roles, notifications
    └── Public (JS/CSS)            ← Form helpers, barcode UX
```

### Data Flow

```
Purchase Order
    │
    ▼
Inbound Shipment ──► Purchase Receipt (ERPNext)
    │                     │
    ▼                     ▼
Putaway Plan          Stock Ledger Entry
    │
    ▼
Warehouse Zone / Bin
    │
    ▼
Sales Order ──► Outbound Shipment ──► Pick List WMS
                    │                      │
                    ▼                      ▼
               Delivery Note         Packing Station
                    │
                    ▼
               Delivery Run ──► RTO / Delivered
```

---

## File Structure

```
wms_erpnext/
├── setup.py
├── requirements.txt
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI/CD
└── wms/
    ├── __init__.py
    ├── hooks.py                    # App entry point
    ├── setup.py                    # Post-migrate setup
    ├── doctype/
    │   ├── warehouse_zone/
    │   │   ├── warehouse_zone.json
    │   │   └── warehouse_zone.py
    │   ├── inbound_shipment/
    │   │   ├── inbound_shipment.json
    │   │   └── inbound_shipment.py
    │   ├── pick_list_wms/
    │   │   ├── pick_list_wms.json
    │   │   └── pick_list_wms.py
    │   ├── outbound_shipment/
    │   │   ├── outbound_shipment.json
    │   │   └── outbound_shipment.py
    │   ├── cycle_count_entry/
    │   │   ├── cycle_count_entry.json
    │   │   └── cycle_count_entry.py
    │   ├── batch_expiry_alert/
    │   │   ├── batch_expiry_alert.json
    │   │   └── batch_expiry_alert.py
    │   └── delivery_run/
    │       ├── delivery_run.json
    │       └── delivery_run.py
    ├── report/
    │   ├── inventory_aging_report/
    │   │   ├── inventory_aging_report.json
    │   │   └── inventory_aging_report.py
    │   ├── pick_accuracy_report/
    │   │   ├── pick_accuracy_report.json
    │   │   └── pick_accuracy_report.py
    │   ├── daily_dispatch_summary/
    │   │   ├── daily_dispatch_summary.json
    │   │   └── daily_dispatch_summary.py
    │   └── zone_utilization/
    │       ├── zone_utilization.json
    │       └── zone_utilization.py
    ├── workspace/
    │   └── wms/
    │       └── wms.json
    ├── fixtures/
    │   ├── roles.json
    │   └── notifications.json
    ├── tasks/
    │   ├── batch_expiry.py
    │   └── cycle_count.py
    └── public/
        ├── js/
        │   └── wms.js
        └── css/
            └── wms.css
```

---

## DocTypes

### 1. Warehouse Zone

**Purpose:** Defines physical zones (Receiving, Storage, Picking, Packing, Dispatch, Cold, Returns) within a warehouse. Each zone contains a bin table and capacity metadata.

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `zone_code` | Data | Unique code (e.g. `STG-A01`) |
| `zone_name` | Data | Human-readable name |
| `warehouse` | Link → Warehouse | Parent ERPNext warehouse |
| `zone_type` | Select | Receiving / Storage / Picking / Packing / Staging / Cold / Return / Dispatch |
| `max_capacity_kg` | Float | Weight capacity limit |
| `current_utilisation_pct` | Percent | Auto-computed from SLE |
| `bins_table` | Table | Child: bin code, type, max qty, current qty, is_locked |
| `priority` | Int | Lower = higher putaway priority |
| `temperature_zone` | Select | Ambient / Chill / Frozen |

**Controller Logic:**
- `validate`: Prevents duplicate bin codes; auto-computes utilisation % from Stock Ledger Entry.
- `get_available_bins()`: Whitelist method for putaway plan API calls.

---

### 2. Inbound Shipment

**Purpose:** End-to-end inbound flow from gate receipt through QC to putaway, creating a Purchase Receipt in ERPNext.

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `supplier` | Link → Supplier | Inbound supplier |
| `purchase_order` | Link → Purchase Order | Source PO |
| `status` | Select | Draft → Received → Inspecting → Putaway Pending → Completed → Rejected |
| `putaway_strategy` | Select | Manual / Auto-Zone Priority / Auto-FEFO / Auto-ABC |
| `putaway_details` | Table | Auto-generated putaway plan rows |
| `linked_purchase_receipt` | Link → PR | Created on submit |

**Workflow:**
```
Submit → status=Received → (QC if required) → status=Putaway Pending → Putaway Done → Completed
                                                                          └── PR auto-created
```

**Controller Logic:**
- `on_submit`: Creates Purchase Receipt from PO, triggers putaway.
- `_auto_generate_putaway_plan()`: Iterates zones by priority, fills bins greedily.
- `mark_qc_complete()`: Whitelist method called from form button.

---

### 3. Pick List WMS

**Purpose:** Flexible picking instruction — supports Single, Batch, Wave, and Cluster pick modes. Tracks picker performance (accuracy %, lines/hour).

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `pick_type` | Select | Single Order / Batch Pick / Wave Pick / Cluster Pick |
| `picker` | Link → User | Assigned warehouse picker |
| `priority` | Select | Normal / High / Urgent |
| `sla_deadline` | Datetime | Required completion time |
| `status` | Select | Draft → Assigned → In Progress → Picked → Short Pick → Cancelled |
| `items` | Table | Pick lines: item, qty, zone, bin, picked_qty |
| `pick_duration_mins` | Float | Auto-calculated on completion |

**Controller Logic:**
- `validate`: Sorts pick lines by zone → bin (travel-path optimisation).
- `start_picking()`: Sets status to In Progress, records start time.
- `confirm_pick_line()`: Updates individual line picked qty, checks if all confirmed.
- `create_delivery_note()`: Creates ERPNext Delivery Note from confirmed picks.

**Short Pick Handling:** If any line `picked_qty < qty`, status becomes `Short Pick` and a notification fires to the WMS Manager.

---

### 4. Outbound Shipment

**Purpose:** Full outbound lifecycle — order release, pick trigger, packing station tracking, carrier manifest, and dispatch.

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `customer` | Link → Customer | Ship-to customer |
| `sales_order` | Link → Sales Order | Source SO |
| `channel` | Select | Website / Amazon / Flipkart / Zepto / Blinkit / B2B / etc. |
| `carrier` | Link → Supplier | 3PL / last-mile carrier |
| `tracking_number` | Data | AWB / courier tracking ID |
| `status` | Select | Draft → Pick Pending → Packing → Manifested → Dispatched → Delivered → RTO |

**Controller Logic:**
- `on_submit`: Auto-creates Pick List WMS with priority based on channel (Zepto/Blinkit = High).
- `manifest_and_dispatch()`: Sets AWB + carrier, transitions to Manifested.
- `mark_dispatched()`: Final status transition.

---

### 5. Cycle Count Entry

**Purpose:** Physical inventory count with system-vs-actual variance capture and one-click Stock Reconciliation submission.

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `count_type` | Select | Full Count / ABC A / B / C / Zone-Specific / Spot Check |
| `items` | Table | Item, system_qty, counted_qty, variance_qty |
| `variance_lines` | Int | Lines with non-zero variance |
| `variance_value` | Currency | Total monetary variance |
| `linked_stock_reconciliation` | Link | Created on reconcile action |

**Controller Logic:**
- `populate_system_qty()`: Pulls latest SLE qty for each item.
- `create_stock_reconciliation()`: Submits ERPNext Stock Reconciliation for all variance lines.

---

### 6. Batch Expiry Alert

**Purpose:** FEFO monitoring. Auto-populated by daily scheduler. Colour-coded alert levels for near-expiry stock. Critical for perishables (grocery, pharma, FMCG).

**Alert Levels:**

| Level | Days to Expiry |
|---|---|
| Green | > 90 days |
| Yellow | 31–90 days |
| Orange | 8–30 days |
| Red | 1–7 days |
| Expired | ≤ 0 days |

---

### 7. Delivery Run

**Purpose:** Groups multiple outbound shipments into a single rider/vehicle run for last-mile dispatch. Models Zepto's rider batching logic.

**Key Fields:**

| Field | Type | Description |
|---|---|---|
| `vehicle` | Data | Vehicle plate / rider ID |
| `driver` | Link → User | Rider/driver |
| `shipments` | Table | Outbound Shipment rows with delivery_status |
| `status` | Select | Draft → Loading → Out for Delivery → Completed / Partial |

**Controller Logic:**
- `start_run()`: Records departure time.
- `complete_run()`: Marks delivered shipments as `Delivered`, failed as `RTO`.

---

## Reports

### 1. Inventory Aging Report

Identifies slow-moving and dead stock by aging bucket (0–30, 31–60, 61–90, 91–180, 180+ days).

**Filters:** Warehouse, Item Group, Min Aging Days

**Key Columns:** Item, Warehouse, Batch, Qty, Valuation Rate, Stock Value, Last Movement, Aging Days, Aging Bucket, Expiry Date, Days to Expiry

---

### 2. Pick Accuracy Report

Measures picker productivity and accuracy. Core KPI for warehouse operations.

**Filters:** Picker, From Date, To Date

**Key Columns:** Pick List, Picker, Pick Type, Total Lines, Picked Lines, Short Lines, Accuracy %, Duration (mins), Lines/Hour

---

### 3. Daily Dispatch Summary

Channel-wise dispatch throughput report. Compares orders received vs dispatched for the day.

**Filters:** Date

**Key Columns:** Channel, Total Orders, Dispatched, RTO, Pending Pack, Dispatch %

---

### 4. Zone Utilization

Real-time zone capacity view. Highlights critical zones (≥90% full).

**Filters:** Warehouse

**Key Columns:** Zone Code, Zone Name, Zone Type, Warehouse, Max Capacity, Utilisation %, Status (Critical / High / Normal / Low)

---

## Workspace

The **WMS Workspace** tab appears in the ERPNext sidebar under the module name `WMS`. It provides:

- **Shortcuts:** Quick links to all WMS DocTypes and Reports.
- **Charts:** Inbound vs Outbound bar chart, Zone Utilisation donut.
- **Organised Sections:** Inbound Ops | Outbound Ops | Inventory Control | Reports.

---

## Notifications

| Notification | Trigger | Recipients |
|---|---|---|
| **Batch Expiry Red Alert** | Batch Expiry Alert: 7 days before expiry_date | WMS Manager, Stock Manager |
| **Pick List Assigned** | Pick List WMS: picker field changed | Assigned picker (by document field) |
| **Inbound Shipment Arrived** | Inbound Shipment: status changed | WMS Manager, WMS Receiver |
| **Zone Capacity Critical** | Warehouse Zone: utilisation ≥ 90% | WMS Manager |
| **Short Pick Alert** | Pick List WMS: status = Short Pick | WMS Manager, Stock Manager |

All notifications support both **Email** and **In-App** (System Notification) delivery via Frappe's Notification DocType.

---

## Scheduled Tasks

| Task | Schedule | Function |
|---|---|---|
| Batch expiry scan | Daily | `wms.tasks.batch_expiry.flag_expiring_batches` |
| Bin replenishment check | Daily | `wms.tasks.replenishment.check_bin_levels` |
| Auto reslot hot items | Hourly | `wms.tasks.slotting.auto_reslot_hot_items` |
| Zone utilisation refresh | Every 15 min | `wms.tasks.zone_utilisation.refresh_zone_capacity` |
| Cycle count plan generation | Daily 2 AM | `wms.tasks.cycle_count.generate_daily_count_plan` |

---

## Roles & Permissions

| Role | Access |
|---|---|
| **WMS Manager** | Full CRUD + submit + cancel on all WMS DocTypes |
| **WMS Receiver** | Read/Write/Submit on Inbound Shipment |
| **WMS Picker** | Read/Write/Submit on Pick List WMS; Read on Outbound |
| **WMS Packer** | Read/Write/Submit on Outbound Shipment |

Assign these roles to users via **HR → Employee → User Roles** or directly in **Settings → User**.

---

## Installation

### Prerequisites

- Python 3.11+
- Frappe Bench
- ERPNext v15 installed on your site

### Step-by-step

```bash
# 1. Navigate to your bench directory
cd /home/frappe/frappe-bench

# 2. Get the app
bench get-app wms https://github.com/your-org/wms_erpnext.git

# 3. Install on your site
bench --site your-site.com install-app wms

# 4. Run migrations
bench --site your-site.com migrate

# 5. Build assets
bench build --app wms

# 6. Restart services
bench restart
```

### Post-Install

After migration, the `after_migrate` hook automatically:
1. Creates the 4 WMS roles.
2. Creates 7 default warehouse zones mapped to your default warehouse.

To manually re-run setup:

```bash
bench --site your-site.com execute wms.setup.setup_roles
bench --site your-site.com execute wms.setup.setup_default_warehouse_zones
```

### Export Fixtures

After customising roles/notifications in the UI:

```bash
bench --site your-site.com export-fixtures --app wms
```

---

## Configuration

### 1. Map Your Warehouse Zones

Go to **WMS → Warehouse Zone** and define your zones. Each zone needs:
- A unique `Zone Code`
- `Warehouse` (ERPNext warehouse)
- `Zone Type`
- Bins in the child table with `bin_code`, `max_qty`

### 2. Set Putaway Strategy

On each **Inbound Shipment**, choose:
- **Manual** – Fill putaway_details rows yourself.
- **Auto - Zone Priority** – System fills bins by zone `priority` field.
- **Auto - FEFO** – Prioritises zones with existing stock of the same item (FEFO).
- **Auto - ABC** – Routes A-class to high-pick zones, C-class to bulk zones.

### 3. Configure Notifications

Go to **Settings → Notification** and enable/customise the 5 WMS notifications. Set email IDs for roles in **HR → Employee**.

### 4. ABC Classification

To enable ABC-based cycle counting, set `abc_classification` (A/B/C) on each **Item** via ERPNext's standard Item DocType (or use the bulk update tool).

### 5. Channel-Based Pick Priority

In `outbound_shipment.py → _auto_create_pick_list()`, the channels `Zepto`, `Blinkit`, and `Swiggy Instamart` auto-set pick priority to `High`. Modify this list to match your SLA requirements.

---

## Extending the App

### Add a New DocType

```bash
bench --site your-site.com new-doctype "My WMS DocType"
```

Or create JSON + Python files manually following the patterns in `wms/doctype/`.

### Add a New Report

1. Create folder: `wms/report/my_report/`
2. Add `my_report.json` (type: Script Report, ref_doctype, filters).
3. Add `my_report.py` with `execute(filters)` returning `(columns, data)`.
4. Run `bench migrate`.

### Add a Scheduled Task

In `hooks.py`, add to `scheduler_events`:

```python
scheduler_events = {
    "daily": [
        "wms.tasks.my_new_task.run",
    ],
}
```

### Custom Fields on ERPNext DocTypes

Use `wms/custom_field/` directory with JSON fixtures, or create via **Customize Form** and export.

---

## FAQ

**Q: Does this replace ERPNext's Stock Module?**
A: No. This app adds a WMS layer on top of ERPNext. All stock movements (Purchase Receipt, Delivery Note, Stock Entry, Stock Reconciliation) are still native ERPNext documents. The WMS app orchestrates the warehouse workflow and then triggers ERPNext's stock documents.

**Q: Can I use this with multi-warehouse setups?**
A: Yes. Each Warehouse Zone is mapped to one ERPNext Warehouse. You can have different sets of zones per warehouse.

**Q: Is barcode scanning supported?**
A: The JS layer (`wms.js`) includes a barcode scan hook (`wms.attach_barcode_scanner`). You can attach this to any field. Full barcode scanner integration requires a compatible USB/Bluetooth scanner that sends keystrokes.

**Q: How does FEFO picking work?**
A: The `Batch Expiry Alert` scheduler flags batches by expiry. When creating a Pick List, you can filter pick lines by batch and sort by `expiry_date ASC`. Full automatic FEFO in pick line generation is on the roadmap.

**Q: Can I use this for dark stores / quick commerce?**
A: Yes – set channel to `Zepto`/`Blinkit`/`Swiggy Instamart` on Outbound Shipments and the system auto-sets pick priority to `High`. Use `Cluster Pick` type for small-basket quick picks.

---

## License

MIT License. See LICENSE file.
