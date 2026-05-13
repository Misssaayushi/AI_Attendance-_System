# Step 3: Hero Section with CTA Buttons

## Goal
Create the central hero area with an icon, a short tagline, and two primary call-to-action buttons.

## Tasks

- [x] **Create `HeroSection.jsx`** in `src/components/home/`
  - Display a centered icon (Lucide `Fingerprint` or `ScanFace`) inside a styled circle.
  - Show a short tagline: e.g., "Smart, secure, and automated attendance tracking."
  - Render two `<Button>` components side-by-side:
    - **"Start Attendance"** → navigates to `/attendance` (primary variant, `size="lg"`).
    - **"Register New User"** → navigates to `/register` (outline variant, `size="lg"`).
  - Use `useNavigate()` from React Router for navigation.
  - Wrap in `<Container>`.

## Design Specs
- Icon container: `p-5 bg-blue-600/20 rounded-full` with a large icon (`size={72}`).
- Tagline: `text-lg text-gray-400`, max-width for readability.
- Buttons: Stack vertically on mobile (`flex-col`), row on tablet+ (`sm:flex-row`), with `gap-4`.
- Section spacing: `py-12 sm:py-16`.
- Center everything with `text-center` and `flex flex-col items-center`.

## Files Affected
| File | Action |
|---|---|
| `src/components/home/HeroSection.jsx` | **Create** |

## Acceptance Criteria
- Icon, tagline, and two buttons are centered and visible.
- Clicking "Start Attendance" navigates to `/attendance`.
- Clicking "Register New User" navigates to `/register`.
- Buttons stack on mobile and sit side-by-side on larger screens.
