# Step 10 – Security Integration

## Goal
Add JWT‑based admin protection to all Student endpoints and outline role‑based access placeholders.

## Files to modify
- `app/dependencies.py` – add `get_current_admin_user` dependency.
- `app/routes/students.py` – include `dependencies=[Depends(get_current_admin_user)]` on router.

## Implementation Notes
- Re‑use existing `oauth2_scheme` from auth module.
- Return 403 if user.role != "admin".
- Document how to extend for future roles.

---
