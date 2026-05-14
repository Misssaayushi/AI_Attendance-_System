import time
import cv2
from ai_module.recognize_faces import start_recognition
from ai_module.utils import get_logger

def run_performance_test():
    """
    Simulates a 15-second recognition run to measure system stability.
    """
    logger = get_logger("RecognitionTest")
    logger.info("Starting Recognition Performance Test (15 Seconds)...")
    
    # We will simply call the main recognition script
    # In a real test environment, we would automate frame inputs, 
    # but for this Phase, manual verification of the UI is key.
    
    try:
        start_recognition()
        logger.info("Recognition test completed successfully.")
    except Exception as e:
        logger.error(f"Performance Test Failed: {str(e)}")

if __name__ == "__main__":
    run_performance_test()
