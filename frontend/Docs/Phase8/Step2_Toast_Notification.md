# Step 2: Global Toast Notification Architecture

## Goal
Construct a robust, non-blocking toast banner alert context supporting successive triggers (success, failure, warnings, alerts).

## Tasks
* [ ] Create the global `ToastContext.jsx` system.
* [ ] Build a floating UI wrapper mapping multiple stacked toast cards.
* [ ] Implement 4 stylized message themes:
  * **Success**: Neon Green theme with Check indicator.
  * **Error**: Crimson Red design with alert indicator.
  * **Warning**: Amber Orange style.
  * **Info**: Ocean Blue layout.
* [ ] Add automatic dismiss timeout triggers (e.g. dismiss after 4 seconds).

## Files Affected
* `src/context/ToastContext.jsx`
* `src/components/ui/ToastContainer.jsx`
* `src/App.jsx`
