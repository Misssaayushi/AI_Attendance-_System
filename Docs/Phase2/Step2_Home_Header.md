# Step 2: Home Header Section

## Goal
Create the top section of the Home page displaying the university name and project title.

## Tasks

- [x] **Create `HomeHeader.jsx`** in `src/components/home/`
  - Display university name in a smaller, muted text (`text-sm uppercase tracking-widest text-gray-400`).
  - Display project title "AI Attendance Management System" as the primary `<h1>` heading.
  - Apply a subtle gradient text effect or a gradient divider line for visual polish.
  - Center all content horizontally.
  - Use `<Container>` for consistent width.

## Design Specs
- Background: Inherit from page (`bg-gray-900`).
- University text: `text-sm`, uppercase, letter-spaced, `text-blue-400`.
- Title: `text-3xl sm:text-4xl lg:text-5xl`, `font-bold`, `text-white`.
- Spacing: `pt-16 pb-8` on the section.
- Optional: A thin gradient line (`h-1 bg-gradient-to-r from-blue-500 to-violet-500`) below the title.

## Files Affected
| File | Action |
|---|---|
| `src/components/home/HomeHeader.jsx` | **Create** |

## Acceptance Criteria
- University name and project title are clearly visible and centered.
- Text scales responsively from mobile to desktop.
- Semantic HTML: uses `<header>` and `<h1>`.
