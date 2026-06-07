# Step 1: Authentication Integration

## 🎯 Objective
Wire the Frontend login/splash screen to the Backend's JWT authentication system so that all subsequent API calls include a valid Bearer token.

---

## 📊 Current State

### Backend (✅ Ready)
- **Login endpoint**: `POST /api/v1/auth/login`
  - Accepts: `{ "username": "...", "password": "..." }`
  - Returns: `{ "success": true, "access_token": "...", "token_type": "bearer", "username": "..." }`
- **Token validation**: `GET /api/v1/auth/me` — returns current admin info
- **Logout**: `POST /api/v1/auth/logout` — client-side token discard
- **All protected routes** use `Depends(get_current_admin)` which extracts JWT from `Authorization: Bearer <token>` header

### Frontend (❌ Not Connected)
- `SYNEXIntro.jsx` has a login form UI but it does **NOT** call the backend
- `api.js` creates an Axios instance but does **NOT** attach auth tokens
- No auth context/state management exists
- No token storage (localStorage/sessionStorage)

---

## 📝 Implementation Tasks

### Task 1.1 — Create AuthContext (`src/context/AuthContext.jsx`)

**Purpose**: Global auth state management with React Context.

**Responsibilities**:
- Store JWT token, username, and `isAuthenticated` flag
- Provide `login(username, password)` function that calls `/api/v1/auth/login`
- Provide `logout()` function that clears token
- Persist token in `localStorage` for session persistence
- Auto-validate token on app load via `/api/v1/auth/me`

```jsx
// Key structure:
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('auth_token'));
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // On mount: validate existing token
  useEffect(() => {
    if (token) {
      validateToken();
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const response = await api.post('/api/v1/auth/login', { username, password });
    const { access_token, username: user } = response.data;
    localStorage.setItem('auth_token', access_token);
    setToken(access_token);
    setUser({ username: user });
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const validateToken = async () => {
    try {
      const response = await api.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser({ username: response.data.username });
      setIsAuthenticated(true);
    } catch {
      logout(); // Token expired/invalid
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ token, user, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

### Task 1.2 — Add Axios Interceptor (`src/services/api.js`)

**Purpose**: Auto-attach JWT token to every outgoing request.

**Changes**:
```diff
 const api = axios.create({
-  baseURL: 'http://localhost:8000',
+  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
   headers: {
     'Content-Type': 'application/json',
   },
 });

+// Request interceptor — attach JWT token
+api.interceptors.request.use((config) => {
+  const token = localStorage.getItem('auth_token');
+  if (token) {
+    config.headers.Authorization = `Bearer ${token}`;
+  }
+  return config;
+});
+
+// Response interceptor — handle 401 (redirect to login)
+api.interceptors.response.use(
+  (response) => response,
+  (error) => {
+    if (error.response?.status === 401) {
+      localStorage.removeItem('auth_token');
+      window.location.href = '/';
+    }
+    return Promise.reject(error);
+  }
+);
```

---

### Task 1.3 — Connect SYNEXIntro Login Form

**File**: `src/components/intro/SYNEXIntro.jsx`

**Changes**:
- Import `useAuth` hook from AuthContext
- Replace the existing `onEnter` callback with actual login logic:
  ```jsx
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      onEnter(); // Transition to dashboard
    } catch (error) {
      setLoginError(error.response?.data?.detail || 'Login failed');
    }
  };
  ```

---

### Task 1.4 — Wrap App with AuthProvider

**File**: `src/App.jsx`

**Changes**:
```diff
+import { AuthProvider } from './context/AuthContext';

 function App() {
   return (
     <ThemeProvider>
       <ToastProvider>
+        <AuthProvider>
           {/* ... existing content ... */}
+        </AuthProvider>
       </ToastProvider>
     </ThemeProvider>
   );
 }
```

---

### Task 1.5 — Add Route Protection

**File**: `src/routes/AppRoutes.jsx`

**Changes**:
- Create a `ProtectedRoute` component that checks `isAuthenticated`
- Redirect unauthenticated users to home/login

```jsx
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/" replace />;
  
  return children;
};
```

---

## ✅ Verification Checklist
- [ ] Login form sends `POST /api/v1/auth/login` with credentials
- [ ] JWT token stored in localStorage on successful login
- [ ] Token attached to all subsequent API requests via interceptor
- [ ] Protected routes redirect to login if no valid token
- [ ] 401 responses trigger automatic logout
- [ ] Page refresh preserves login state (token validation on mount)
- [ ] Logout clears token and redirects to login

---

## 📁 Files Changed
| File | Action |
|---|---|
| `src/context/AuthContext.jsx` | **NEW** |
| `src/services/api.js` | **MODIFY** — add interceptors |
| `src/components/intro/SYNEXIntro.jsx` | **MODIFY** — connect login |
| `src/App.jsx` | **MODIFY** — wrap AuthProvider |
| `src/routes/AppRoutes.jsx` | **MODIFY** — add ProtectedRoute |
