# Step 04 — Utility Enhancements

## 🎯 Objective
Add helper utilities for common database operations to ensure consistency and clean code.

---

## 📌 Implementation Details

### 1. Transaction Helper
- A utility to safely handle `commit()` and `rollback()` logic.

### 2. Query Logger
- An enhancement to the Phase 1 logger to specifically capture slow SQL queries or connection timeouts.

---

## ✅ Checklist
- [ ] Add DB session helper to `app/utils/`.
- [ ] Integrate DB logs with `app/utils/logger.py`.
