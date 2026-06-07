# Step 4: Project Info Cards Section

## Goal
Create a section displaying 3 professional benefit/info cards that explain the system's purpose.

## Tasks

- [x] **Create `InfoCard.jsx`** in `src/components/home/`
  - A reusable card component accepting props: `icon`, `title`, `description`.
  - Uses the existing `<Card>` component as a base wrapper.
  - Renders the Lucide icon inside a colored circle, the title as `<h3>`, and description as `<p>`.

- [x] **Create `InfoSection.jsx`** in `src/components/home/`
  - A section component that renders a heading ("Why AI Attendance?") and a grid of 3 `<InfoCard>` components.
  - Card content:
    1. **AI-Powered Recognition** — "Leverages OpenCV-based facial recognition for instant, contactless attendance marking."
    2. **Secure & Reliable** — "Tamper-proof records stored in a MySQL database with real-time sync and audit trails."
    3. **Real-Time Analytics** — "Live dashboard with attendance trends, late arrival tracking, and exportable reports."
  - Uses `<Container>` for consistent width.

## Design Specs
- Section heading: `text-2xl sm:text-3xl font-bold text-white text-center`, with `mb-8`.
- Grid: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`.
- InfoCard icon circle: `p-3 rounded-full` with tinted background (e.g., `bg-blue-500/20 text-blue-400`).
- Each card icon uses a different accent color (blue, green, violet) for visual variety.
- Section spacing: `py-12 sm:py-16`.

## Files Affected
| File | Action |
|---|---|
| `src/components/home/InfoCard.jsx` | **Create** |
| `src/components/home/InfoSection.jsx` | **Create** |

## Acceptance Criteria
- Three cards are displayed in a responsive grid (1-col → 2-col → 3-col).
- Each card has a unique icon and color accent.
- `<InfoCard>` can be reused independently on other pages.
