import time
from datetime import datetime
from ai_module.utils import AttendanceManager, get_logger

def run_verification_test():
    logger = get_logger("VerificationTest")
    logger.info("Starting Attendance Verification Logic Test...")

    # Initialize manager with short cooldown for testing
    mgr = AttendanceManager(cooldown_minutes=0.1, min_confidence=80, stability_frames=3)

    test_student_id = "test_001"
    test_name = "Test Student"

    # 1. Test Stability
    logger.info("TEST 1: Stability Streak")
    for i in range(1, 4):
        verified, msg = mgr.verify_attendance(test_student_id, test_name, 90)
        logger.info(f"Frame {i}: Verified={verified}, Msg={msg}")

    # 2. Test Cooldown
    logger.info("TEST 2: Cooldown Logic")
    verified, msg = mgr.verify_attendance(test_student_id, test_name, 90)
    logger.info(f"Instant Re-scan: Verified={verified}, Msg={msg}")

    # 3. Test Confidence Threshold
    logger.info("TEST 3: Low Confidence Rejection")
    verified, msg = mgr.verify_attendance("other_id", "Weak Match", 50)
    logger.info(f"Low Confidence (50%): Verified={verified}, Msg={msg}")

    # 4. Test Unknown Person
    logger.info("TEST 4: Unknown Person Handling")
    verified, msg = mgr.verify_attendance("unknown", "Unknown Person", 0)
    logger.info(f"Unknown Result: Verified={verified}, Msg={msg}")

    logger.info("Verification logic test complete.")

if __name__ == "__main__":
    run_verification_test()
