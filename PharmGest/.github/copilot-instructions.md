# PharmGest AI Coding Instructions

## Project Overview
PharmGest is a desktop pharmacy management ERP system built with **PyQt6** (GUI) and **SQLAlchemy + SQLite** (database). It handles inventory management, POS operations, sales history, and invoice generation. Role-based access (admin/seller) controls feature visibility.

## Architecture & Key Components

### 1. **Entry Point & Authentication**
- [src/pharmgest/main.py](src/pharmgest/main.py): Application bootstrap with `LoginDialog` → `MainWindow` flow
- User role/name passed from login → propagated to all UI components
- Always check `user_role` before enabling admin-only features (inventory editing, product creation)

### 2. **Database Layer**
- [src/pharmgest/config/database.py](src/pharmgest/config/database.py): SQLAlchemy setup with SQLite + WAL mode optimization
- **Critical pattern**: Use `get_db_session()` context manager (NOT bare `SessionLocal()`) to ensure rollback on errors
- [src/pharmgest/database/models.py](src/pharmgest/database/models.py) defines: `User`, `Category`, `Product`, `ProductBatch`, `Sale`, `SaleDetail`

### 3. **Data Model Specifics**
- **Product model**: Supports fractional stock via `is_fractionable` + `units_per_box`; has `stock_display` property for UI formatting
- **ProductBatch model**: New table linking products to batches (`batch_code`, `stock`, `expiry_date`) — enables lot tracking
- **Sales**: `Sale` (header) → `SaleDetail` (line items with `is_box_sale` flag to track box vs. unit sales)
- Total product stock = sum of all batch stocks (accessed via relationship `product.batches`)

### 4. **Configuration**
- [src/pharmgest/config/settings.py](src/pharmgest/config/settings.py): Centralized constants (stock thresholds, colors, limits)
- Stock thresholds: `STOCK_CRITICO = 20`, `STOCK_BAJO = 50` → trigger UI color warnings
- Logging setup: [src/pharmgest/config/logging_config.py](src/pharmgest/config/logging_config.py) — all components use `logger`

### 5. **UI Layer**
- [src/pharmgest/ui/main_window.py](src/pharmgest/ui/main_window.py): Tab-based interface (InventoryWidget, POSWidget, SalesHistoryWidget)
- **Stock traffic light**: Products colored in red (critical) or yellow (low) based on `total_stock`
- Dialogs: [src/pharmgest/ui/dialogs/product_dialog.py](src/pharmgest/ui/dialogs/product_dialog.py), [batch_dialog.py](src/pharmgest/ui/dialogs/batch_dialog.py), [login_dialog.py](src/pharmgest/ui/dialogs/login_dialog.py)

### 6. **Services**
- [src/pharmgest/services/invoice.py](src/pharmgest/services/invoice.py): PDF generation via ReportLab; saves to `facturas/` folder with naming `factura_{sale_id}.pdf`

## Development Workflows

### Initialize Project
```bash
python create_db.py          # Create fresh database
python create_seller.py      # Add test seller user
python seed_data.py          # Populate sample data
```

### Run Application
```bash
python src/pharmgest/main.py
```

### Database Schema Updates
- Modify models in [database/models.py](src/pharmgest/database/models.py)
- Run [update_db_schema.py](src/pharmgest/update_db_schema.py) to apply migrations (or recreate with `create_db.py`)

## Project-Specific Patterns

### Session Management
**Always use the context manager**, not raw `SessionLocal()`:
```python
from src.pharmgest.config.database import get_db_session

with get_db_session() as session:
    product = session.query(Product).filter(...).first()
    # Session auto-commits on exit; rollbacks on exception
```

### Role-Based UI Control
```python
if self.user_role == "admin":
    # Show admin-only buttons (add product, manage stock, etc.)
    btn_add = QPushButton("➕ Nuevo Producto")
else:
    # Sellers see read-only or limited views (POS, history)
```

### Stock Display with Fractional Units
```python
# Product.stock_display property formats intelligently:
# - Non-fractionable: "120 Unid."
# - Fractionable (e.g., units_per_box=12): "10 Cajas / 0 Sueltas"
stock_text = product.stock_display  # Use this in UI, not raw totals
```

### PDF Invoice Generation
Takes `sale_id`, `items` list (dicts with `qty`, `name`, `price`, `subtotal`), `total`, `user_name`.
Returns file path; auto-creates `facturas/` folder.

## Critical Gotchas
1. **Batch relationships**: Product stock derives from batch records; direct stock manipulation bypasses batch tracking
2. **WAL mode**: SQLite pragmas in [database.py](src/pharmgest/config/database.py) are essential for GUI responsiveness — don't remove
3. **Role enforcement**: Always validate `user_role` server-side before allowing operations; UI controls alone are insufficient
4. **Logging**: Use the configured logger from `config/logging_config.py` for all errors/debug output

## Key Files for Common Tasks
- **Add new product field**: [models.py](src/pharmgest/database/models.py) (add Column), [settings.py](src/pharmgest/config/settings.py) (add constant if threshold-based)
- **New POS feature**: Extend [pos_widget.py](src/pharmgest/ui/pos_widget.py) + modify [invoice.py](src/pharmgest/services/invoice.py) if invoice changes needed
- **Admin-only dialog**: Create in [ui/dialogs/](src/pharmgest/ui/dialogs/), add tab to [main_window.py](src/pharmgest/ui/main_window.py), guard with `if user_role == "admin"`
