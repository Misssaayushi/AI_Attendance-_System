# Phase 1: Frontend Architecture & Foundation Implementation Plan

## 1. Overall Frontend Architecture
The application will be built as a Single Page Application (SPA) using **React** with the **Vite** build tool. This approach ensures rapid development, immediate hot-module replacement (HMR), and a highly optimized production build. 
Since the backend is built with **FastAPI**, our API service layer (using Axios) will be structured to easily handle JSON requests/responses and standard FastAPI features (like Bearer Token authentication and standard HTTP status codes). The architecture emphasizes separation of concerns: routing is handled at the top level, views (pages) are assembled from reusable components, and API calls are abstracted into a dedicated services layer.

## 2. Folder Structure Explanation
We will adhere to a modular and scalable structure to ensure long-term maintainability:

```text
frontend/
├── src/
│   ├── assets/        # Static files like images, SVGs, and global CSS.
│   ├── components/    # Reusable, stateless UI components (Buttons, Cards, Inputs).
│   ├── layouts/       # Structural components (Sidebar, Navbar, MainLayout).
│   ├── pages/         # Route-level components representing distinct screens.
│   ├── routes/        # Route definitions and configuration (centralized routing).
│   ├── services/      # API communication layer (Axios instances, endpoint calls to FastAPI).
│   ├── utils/         # Helper functions (e.g., date formatters).
│   ├── App.jsx        # Root component bridging context providers and routing.
│   └── main.jsx       # Entry point, rendering the App into the DOM.
```
**Why this structure?** It naturally separates the "what it looks like" (components/layouts) from "what it does" (services/pages), making it easy for multiple developers to collaborate without merge conflicts.

## 3. Routing Strategy
We will use **React Router DOM v6**. 
- **Centralized Routing**: Routes will be defined in a dedicated `routes/` directory to keep `App.jsx` clean.
- **Layout Wrappers**: We will utilize nested routing. A parent `MainLayout` component will wrap pages like `/dashboard`, `/records`, and `/attendance` to provide consistent navigation (sidebar/navbar), while `/` and `/register` may use a simpler `AuthLayout` or stand alone.
- **Protected Routes (Future-proofing)**: While not fully implemented in Phase 1, the routing structure will be designed to easily accommodate an `AuthGuard` wrapper component later.

## 4. Component Structure
Components will follow the **Atomic Design principle** loosely:
- **Atoms**: `Button`, `InputField`, `Typography` (residing in `components/`).
- **Molecules**: `FormGroup`, `UserCard` (combining atoms).
- **Organisms/Layouts**: `Sidebar`, `Navbar` (residing in `layouts/`).
- **Templates/Pages**: `Dashboard`, `Home` (residing in `pages/`).
We will stick exclusively to functional components utilizing React Hooks.

## 5. Tailwind Setup Approach
We will configure **Tailwind CSS** as our primary styling engine.
- **Global Theme Configuration**: `tailwind.config.js` will be heavily customized with a specific dark-themed color palette (e.g., `bg-gray-900`, accents in indigo or teal), custom fonts (Inter/Roboto), and spacing scales.
- **Directives**: Standard `@tailwind` directives will be added to `index.css`.
- **Utility-First**: We will avoid creating custom CSS classes unless absolutely necessary for complex animations or specific pseudo-elements that Tailwind struggles with.

## 6. Reusable UI Strategy
To maintain a professional UI foundation without code duplication:
- **Base Components**: We will create foundational components like `<Button />` with variant props (e.g., `variant="primary" | "secondary" | "outline"`).
- **Consistency**: By enforcing the use of these base components across all pages, any future design changes only require updating the core component.
- **Card System**: A reusable `<Card />` component will be created to house dashboard widgets and forms, ensuring consistent padding, border-radius, and shadows.

## 7. State Management Approach
For Phase 1 and the foreseeable future, we will prioritize simplicity:
- **Local State**: Managed via `useState` and `useReducer` for component-specific data (e.g., form inputs, toggles).
- **Global UI State**: If needed (e.g., sidebar toggle), we will use React's built-in **Context API**.
- **Server State**: While Redux is an option, given FastAPI's speed and standard JSON responses, handling server state through standard Axios calls inside `useEffect` (or later integrating React Query/SWR) is preferred to avoid over-engineering.

## 8. Responsive Design Strategy
The application will be Mobile-First.
- Tailwind's responsive modifiers (`sm:`, `md:`, `lg:`) will be utilized extensively.
- The base layout will default to a 100% width column flow for mobile, expanding to a grid or sidebar-main layout for desktop (`md:` and above).
- The Homepage and interactive elements will be tested to ensure touch targets are appropriately sized for mobile devices.

## 9. Recommended Dependencies
- `react`, `react-dom` (Core)
- `react-router-dom` (Routing)
- `tailwindcss`, `postcss`, `autoprefixer` (Styling)
- `axios` (API requests, configured for FastAPI)
- `chart.js`, `react-chartjs-2` (For Phase 3/Dashboard analytics)
- `lucide-react` (For clean, consistent, customizable SVG icons)

## 10. Step-by-Step Development Workflow (Phase 1 Execution)
1. **Scaffold Project**: Run `npm create vite@latest frontend -- --template react`.
2. **Install Dependencies**: Install Tailwind CSS, React Router, and Axios.
3. **Configure Tailwind**: Setup `tailwind.config.js` and `index.css` for the dark theme.
4. **Build Folder Structure**: Create the required directories (`components`, `pages`, `layouts`, etc.).
5. **Create Base UI Components**: Build the reusable `<Button />` and `<Card />` components.
6. **Create Layouts**: Build a basic `MainLayout` shell.
7. **Create Placeholder Pages**: Scaffold `Home.jsx`, `Register.jsx`, `Attendance.jsx`, `Dashboard.jsx`, and `Records.jsx`.
8. **Setup Routing**: Wire up the pages in `App.jsx` using `react-router-dom`.
9. **Final Review**: Ensure all routes resolve correctly, the theme is applied globally, and the application builds without errors.
