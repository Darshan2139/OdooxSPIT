# StockMaster - Quick Start Guide

## 🚀 Start the Application

```bash
python app.py
```

The app will run at: `http://localhost:5000`

---

## 🔐 Login Credentials

### Admin Account (Full Access - Inventory Manager)
```
Email: admin@stockmaster.com
Password: admin123
```
✅ Can create/edit/delete Categories & Suppliers

### Staff Account (Limited Access - Warehouse Staff)
```
Email: staff@stockmaster.com
Password: staff123
```
❌ Cannot create Categories & Suppliers (Access Denied)

---

## 📱 Main Navigation

Once logged in, you'll see the top navbar with:

| Link | Purpose |
|------|---------|
| **Dashboard** | View KPIs, recent activities, low stock items |
| **Operations** | Manage Receipts & Deliveries |
| **Products** | View & edit stock (editable cells) |
| **Move History** | View stock ledger with List/Kanban toggle |
| **Settings** | Manage Warehouses, Locations, Categories, Partners |

---

## ⭐ Key Features to Test

### 1. **Editable Stock Cells** (Stock Page)
- Click on any "On Hand" cell
- Type new quantity
- Press Enter to save
- Cell updates instantly

### 2. **Search Modal** (🔍 icon in navbar)
- Click search icon
- Beautiful modal appears
- Enter search term
- Press Enter or click Search
- Context-aware (searches current page)

### 3. **Profile Menu** (👤 icon in navbar)
- Click profile icon
- Dropdown menu appears
- Options: My Profile, Edit Profile, Change Password, Logout

### 4. **List/Kanban Toggle** (Move History page)
- Click "List" button for table view
- Click "Kanban" button for column view
- IN movements (green) | OUT movements (red)

### 5. **Create Categories** (Settings → Categories)
- **Login as Admin first!**
- Click "Create Category" button
- Fill in Name & Description
- Click Save

### 6. **Create Suppliers** (Settings → Partners)
- **Login as Admin first!**
- Click "Create Partner" button
- Fill in Name, Type (Supplier), Email, Phone, Address
- Click Save

---

## 🎯 Complete Testing Workflow

### Phase 1: Authentication (5 min)
```
1. Go to http://localhost:5000
2. Click "Sign Up" → Create new account
3. Login with new account
4. Logout
5. Login with admin@stockmaster.com / admin123
```

### Phase 2: Dashboard (5 min)
```
1. View Dashboard
2. Check KPI cards
3. View Receipt & Delivery cards
4. View Low Stock Products
5. View Recent Activities
```

### Phase 3: Stock Management (10 min)
```
1. Go to Products (Stock page)
2. Click on "On Hand" cell → Edit quantity
3. Use search icon (🔍) → Search for product
4. Filter by category
5. Click View on any product
```

### Phase 4: Warehouse & Location (10 min)
```
1. Go to Settings → Warehouses
2. Click "Create Warehouse" → Add warehouse
3. Click on warehouse → View locations
4. Click "Create Location" → Add location
5. Edit/Delete locations
```

### Phase 5: Categories (5 min) - Admin Only
```
1. Go to Settings → Categories
2. Click "Create Category" → Add category
3. Edit category
4. Try to delete (will fail if used by products)
```

### Phase 6: Suppliers/Partners (5 min) - Admin Only
```
1. Go to Settings → Partners
2. Click "Create Partner" → Add supplier
3. Fill in: Name, Type (Supplier), Email, Phone, Address
4. Click Save
5. View partner details
```

### Phase 7: Receipts (10 min)
```
1. Go to Operations → Receipts
2. Click "NEW" → Create receipt
3. Select supplier (created in Phase 6)
4. Add products & quantities
5. Click Save
6. View receipt details
7. Change status: Draft → Waiting → Ready → Done
```

### Phase 8: Deliveries (10 min)
```
1. Go to Operations → Deliveries
2. Click "NEW" → Create delivery
3. Select customer
4. Add products & quantities
5. Click Save
6. View delivery details
7. Change status: Draft → Picking → Packing → Ready → Done
```

### Phase 9: Move History (5 min)
```
1. Go to Move History
2. View list of all stock movements
3. Click "Kanban" button → View as columns
4. Click "List" button → Return to table
5. Filter by product/location/operation
```

### Phase 10: Search & Profile (5 min)
```
1. Click search icon (🔍) in navbar
2. Search for a product
3. Click profile icon (👤) in navbar
4. View profile menu
5. Click "Change Password"
6. Click "Logout"
```

---

## 🎨 UI Features

### Color Scheme
- **Primary:** #003366 (Dark Blue)
- **Success:** #28a745 (Green) - for IN movements
- **Danger:** #dc3545 (Red) - for OUT movements
- **Warning:** #ffc107 (Yellow) - for warnings

### Responsive Design
- **Desktop:** Full width layout
- **Tablet:** Optimized for 768px width
- **Mobile:** Optimized for 375px width

### Interactive Elements
- ✅ Rounded buttons with hover effects
- ✅ Cards with shadows
- ✅ Smooth transitions
- ✅ No underlines on links
- ✅ Editable table cells
- ✅ Modal dialogs
- ✅ Dropdown menus

---

## 🔍 Troubleshooting

### "Access Denied" on Categories/Partners
**Solution:** Login as admin@stockmaster.com (Inventory Manager role required)

### Can't edit stock quantity
**Solution:** Click directly on the "On Hand" cell (not the row)

### Search doesn't work
**Solution:** Make sure you're on Stock, Receipts, Deliveries, or Move History page

### Can't create supplier in receipt form
**Solution:** Create supplier first in Settings → Partners

### Button has underline
**Solution:** Refresh page (Ctrl+F5) to clear cache

### Database error
**Solution:** Delete `stockmaster.db` and restart app to reset database

---

## 📊 Database Models

```
User (id, name, email, password, role)
  ├─ Warehouse (id, name, code, address, city, state, zip_code, country, phone, email)
  │  ├─ Location (id, warehouse_id, name, code, description)
  │  └─ ProductLocation (id, product_id, location_id, quantity)
  ├─ Category (id, name, description)
  ├─ Product (id, category_id, name, sku, description, min_stock, active)
  ├─ Partner (id, name, type, email, phone, address, city, state, zip_code, country)
  ├─ Receipt (id, receipt_number, date, supplier_id, warehouse_id, location_id, state, notes)
  │  └─ ReceiptLine (id, receipt_id, product_id, quantity, received_qty)
  ├─ Delivery (id, delivery_number, date, customer_id, warehouse_id, location_id, state, notes)
  │  └─ DeliveryLine (id, delivery_id, product_id, quantity, picked_qty, packed_qty)
  ├─ Transfer (id, transfer_number, date, source_location_id, destination_location_id, state)
  │  └─ TransferLine (id, transfer_id, product_id, quantity, transferred_qty)
  ├─ Adjustment (id, adjustment_number, date, product_id, location_id, recorded_qty, counted_qty, state)
  └─ StockLedger (id, date, product_id, location_id, operation_type, quantity_in, quantity_out, balance, reference, partner_id)
```

---

## 📞 Support

For detailed testing instructions, see: **TESTING_GUIDE.md**
For feature status, see: **FEATURE_STATUS.md**

---

**Happy Testing! 🎉**
