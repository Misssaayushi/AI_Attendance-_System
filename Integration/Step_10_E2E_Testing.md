# Step 10: End-to-End Testing & Validation

## 🎯 Objective
Verify that the entire system functions smoothly as a unified application. This final step validates the full data flow from the Frontend UI to the Backend Database to the AI Module, and back again.

---

## 🧪 E2E Test Scenarios

### Scenario 1: Authentication & Protection
| Action | Expected Result |
|---|---|
| Open Frontend without logging in | Directed to SYNEXIntro login screen |
| Enter invalid credentials | Error toast: "Login failed / Invalid credentials" |
| Enter valid admin credentials | Redirected to Dashboard |
| Refresh the Dashboard page | Remains logged in (token validated on mount) |
| Click "Logout" | Token cleared, redirected to login screen |

### Scenario 2: Student Registration
| Action | Expected Result |
|---|---|
| Navigate to Register page | Camera feed opens successfully |
| Fill form, capture face, click Register | Success toast appears |
| Check Backend Database | New student row in `students` table |
| Check AI Module Folder | `dataset/{id}_{name}` folder created with 5+ face images |
| Check AI Module Process | AI logs indicate encoding cache reloaded successfully |

### Scenario 3: Real-Time Attendance
| Action | Expected Result |
|---|---|
| Open Attendance Terminal | UI shows "AI Standby", live feed ready |
| Start AI Module `recognize_faces.py` | UI status changes to "AI Active" |
| Step in front of webcam | AI Module window draws green box with name & confidence |
| Check Frontend UI | "Attendance Marked" toast appears |
| Check Activity Feed | New entry appears instantly (via WebSocket) |

### Scenario 4: Duplicate Prevention
| Action | Expected Result |
|---|---|
| Step in front of webcam *again* | AI Module window shows "Cooldown Active" |
| Check Frontend UI | *No new toast*, no duplicate entry in Activity Feed |
| Check Backend Logs | Log shows duplicate rejected (if AI sends it anyway) |

### Scenario 5: Dashboard Analytics
| Action | Expected Result |
|---|---|
| Check Dashboard Stat Cards | "Present Today" count increased by 1 |
| Check Dashboard Charts | Weekly/Monthly trend charts update with new data |
| Check Student Table | Total student count is correct |

### Scenario 6: Records & Export
| Action | Expected Result |
|---|---|
| Navigate to Records page | New attendance record appears in the table |
| Search for the student | Table filters to show only their records |
| Click "Export CSV" | CSV file downloads |
| Open CSV file | File contains correct column headers and the new record |

### Scenario 7: Resilience & Error Handling
| Action | Expected Result |
|---|---|
| Stop Backend server | Frontend shows red "Cannot connect to Backend" banner |
| Stop Backend server | AI Module continues running, queues attendance events |
| Restart Backend server | Frontend banner disappears |
| Restart Backend server | AI Module successfully replays queued events |

---

## 🛠️ Performance Budgets

Monitor the system to ensure it meets these performance thresholds:

| Metric | Target |
|---|---|
| **Frontend Load Time** | < 1.5 seconds |
| **API Response Time** | < 200 ms (avg) |
| **WebSocket Latency** | < 50 ms |
| **AI Module Frame Rate** | > 15 FPS (even during recognition) |
| **Attendance Loop Time** | < 500 ms (from face detected to UI updated) |

---

## 📦 Final Presentation Checklist

Before the live university demonstration, verify:
- [ ] Database is clean (`DELETE FROM attendance;` if starting fresh)
- [ ] At least 3 students are pre-registered with encodings
- [ ] Admin password is known and documented
- [ ] `API_MOCK_MODE` is set to `false` in AI Module `.env`
- [ ] `VITE_API_BASE_URL` is correct in Frontend `.env`
- [ ] Camera is positioned correctly with good lighting
- [ ] All three services are running (Frontend, Backend, AI Module)

---

## 📁 Files Changed
*None. This is a testing guide.*
