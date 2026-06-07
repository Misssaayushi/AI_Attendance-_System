# Step 03 — Database Initialization

## 🎯 Objective
Create a reusable initialization workflow to verify connections and create tables automatically.

---

## 📌 Implementation Details

### 1. The `init_db` Function
- Check if the database specified in `.env` exists.
- Use `Base.metadata.create_all(bind=engine)` to create all defined tables.
- This function will be called in `app/main.py` during the `startup` event.

### 2. Startup Validation
- Extend the Phase 1 startup check to not just check the connection, but also ensure the table schema is correct.

---

## ✅ Checklist
- [ ] Implement `init_db` in `app/database/connection.py`.
- [ ] Update `app/main.py` to trigger table creation.
- [ ] Verify logs show table creation status.
