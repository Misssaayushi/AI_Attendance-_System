# Phase 3: Student Registration Wizard — Implementation Plan

## Overview
Develop a professional, multi-step registration system to enroll students. This phase focuses on data integrity, high-tech UI for face capture, and preparing data for the FastAPI backend.

---

## 1. UI Structure Strategy
The registration will use a **Stepper Layout** to guide the user:
- **Step 1: Student Details** (The 10 fields you requested).
- **Step 2: Face Enrollment** (Live camera feed with face guide).
- **Step 3: Confirmation** (Data review and final submit).

## 2. Form Field Specification
The following fields will be implemented with validation:
1.  **Full Name** (Text)
2.  **Student ID** (Text/Alphanumeric)
3.  **Email Address** (Email)
4.  **Contact Number** (Tel)
5.  **Department** (Dropdown: CS, IT, ME, EE, etc.)
6.  **Year/Batch** (Dropdown: 2022-2026, etc.)
7.  **Semester** (Select: 1-8)
8.  **Section** (Text: e.g., A, B, C)
9.  **Gender** (Select: Male, Female, Other)
10. **Course** (Text: e.g., B.Tech, M.Tech)

## 3. Component Breakdown
- `RegistrationWizard`: Main container managing the current step.
- `StepIndicator`: Visual progress tracker.
- `DetailsForm`: Component containing the 10 input fields.
- `BiometricCapture`: Component handling the webcam and face guide.
- `RegistrationSummary`: Review screen before submission.

## 4. State Management
We will use a single `formData` object in the parent component to keep track of all inputs, ensuring that data is preserved when moving between steps.

## 5. Technical Integration
- **Form Validation**: Using simple state-based checks or a library if needed.
- **Service Layer**: Prep for `POST /register` to FastAPI.
