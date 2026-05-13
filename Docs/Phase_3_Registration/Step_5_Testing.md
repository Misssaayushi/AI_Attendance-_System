# Step 5: Testing & Verification

## Objective
Create a test script that verifies the entire registration pipeline end-to-end and validates the generated encoding files.

## Tasks
- Create `ai_module/tests/test_registration.py`.
- Test 1: Run a mock registration (capture 5 samples instead of 20 for speed).
- Test 2: Verify that images were saved to the correct dataset folder.
- Test 3: Run encoding generation and verify `.pkl` files were created.
- Test 4: Load an encoding file and confirm it contains valid 128D numpy arrays.
- Test 5: Verify `all_encodings.pkl` contains the correct number of entries.

## Expected Outcome
Full confidence that the registration pipeline produces valid, usable data for Phase 4.
