# Step 5: Assemble Final Home Page

## Goal
Rewrite `Home.jsx` to compose all the new section components into the final landing page.

## Tasks

- [x] **Rewrite `src/pages/Home.jsx`**
  - Remove the old placeholder content.
  - Import and render sections in order:
    1. `<HomeHeader />`
    2. `<HeroSection />`
    3. `<InfoSection />`
  - Add a minimal footer at the bottom with project credit text.
  - Wrap the entire page in a `<main>` tag with `min-h-screen bg-gray-900`.

- [x] **Add a simple footer** (inline in Home.jsx or as a small component)
  - Text: "Built with ❤ for [University Name] — 2026"
  - Styling: `text-center text-sm text-gray-500 py-8 border-t border-gray-800`.

## Files Affected
| File | Action |
|---|---|
| `src/pages/Home.jsx` | **Rewrite** |

## Acceptance Criteria
- Home page renders all 4 sections (Header → Hero → Info → Footer) in order.
- Page scrolls smoothly with proper section spacing.
- No leftover placeholder content from Phase 1.
- The full page looks cohesive and professional.
