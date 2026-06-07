# 🛠️ AI Attendance System: Technical Integration Guide

## 📌 Overview
This document provides the technical specifications required to connect the **AI Recognition Module** with the **Backend (FastAPI/MySQL)** and **Frontend (React)**.

---

## 1. 🖥️ Backend Developer Requirements (FastAPI / MySQL)

The AI Module expects an API endpoint to be available for saving attendance records.

### A. Required API Endpoint
*   **URL**: `/api/v1/attendance/verify`
*   **Method**: `POST`
*   **Request Body (JSON)**:
    ```json
    {
      "student_id": "1",
      "name": "Aayushi",
      "confidence": 92.5,
      "timestamp": "2026-05-16T11:05:00Z",
      "status": "Present"
    }
    ```
*   **Expected Response**: `200 OK` or `201 Created`

### B. Database Schema (MySQL)
Your `attendance` table MUST include these columns to match the AI data:
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INT (PK) | Auto-increment ID |
| `student_id` | VARCHAR(50) | Matches the ID from the AI filename |
| `confidence` | FLOAT | The AI's certainty score (0-100) |
| `timestamp` | DATETIME | When the face was verified |

---

## 2. 🎨 Frontend Developer Requirements (React)

The Frontend must be able to display the results of the AI module.

### A. Real-Time Activity Feed
The frontend should have a component that "listens" (via WebSocket or Polling) for new entries in the database and displays a notification:
*   **Target Component**: `ActivityFeed.jsx`
*   **Visual**: Show a "Success" toast or a new row in a table whenever a student is verified.

### B. Registration Sync
The Frontend must ensure that when a new student is registered:
1.  A folder is created in `ai_module/dataset/` named `{id}_{name}`.
2.  The `id` matches the `student_id` in the MySQL `students` table.

---

## 3. 🔑 Key Integration Standards

To prevent the system from breaking, follow these three rules:

1.  **ID Consistency**: The `student_id` must ALWAYS be the primary key. If the AI detects "1_Aayushi", the ID sent to the backend will be `"1"`.
2.  **Cooldown Handling**: The AI Module already handles "double-marking" protection. The Backend does not need to worry about filtering duplicate scans within a short window.
3.  **Error States**: If the AI sends an "Unknown Person" event, the Backend should decide whether to ignore it or log it as a "Security Alert."

---

## 🚀 Integration Workflow
1.  **Backend Dev**: Build the `/verify` endpoint and the MySQL table.
2.  **AI Module**: We will update the `api_connector.py` to point to the Backend URL.
3.  **Frontend Dev**: Update the dashboard to fetch the latest logs from the Backend.
