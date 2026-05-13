# Step 1: Reusable Foundation Components

## Goal
Build/enhance the reusable components that all Phase 2 sections depend on.

## Tasks

- [x] **Create `Container.jsx`** in `src/components/`
  - A simple wrapper component providing consistent `max-width`, horizontal padding, and centering.
  - Props: `children`, `className` (for overrides).
  - Default classes: `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8`.

- [x] **Enhance existing `Button.jsx`**
  - Add a `size` prop supporting `sm`, `md` (default), `lg`.
  - `lg` size: `px-6 py-3 text-lg` — used for hero CTA buttons.
  - `sm` size: `px-3 py-1.5 text-sm` — for compact actions.
  - Ensure all existing usages remain unaffected (default = `md`).

## Files Affected
| File | Action |
|---|---|
| `src/components/Container.jsx` | **Create** |
| `src/components/Button.jsx` | **Modify** (add size prop) |

## Acceptance Criteria
- `<Container>` wraps content with a consistent max-width on all pages.
- `<Button size="lg">` renders visibly larger than the default.
- No regressions on existing pages using `<Button>`.
