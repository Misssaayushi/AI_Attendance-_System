import pickle
import numpy as np
from pathlib import Path
from ai_module.config import ENCODINGS_DIR, ENCODING_FILE, DATASET_DIR
from ai_module.utils import get_logger

def verify_registration_data():
    logger = get_logger("RegistrationTest")
    logger.info("Starting Registration Verification...")

    # 1. Check Dataset
    student_folders = [f for f in DATASET_DIR.iterdir() if f.is_dir()]
    logger.info(f"Verified {len(student_folders)} student folders in dataset.")

    # 2. Check Individual Encoding Files
    pkl_files = list(ENCODINGS_DIR.glob("*.pkl"))
    # Subtract 1 for the consolidated encodings.pickle if it exists
    individual_pkls = [f for f in pkl_files if f.name != "encodings.pickle"]
    
    logger.info(f"Verified {len(individual_pkls)} individual encoding files.")

    # 3. Validate Consolidated File
    if not ENCODING_FILE.exists():
        logger.error("Consolidated encoding file 'encodings.pickle' NOT found!")
        return

    try:
        with open(ENCODING_FILE, "rb") as f:
            data = pickle.load(f)
        
        encodings = data.get("encodings", [])
        names = data.get("names", [])

        logger.info(f"Consolidated file contains {len(encodings)} total encoding vectors.")
        
        if len(encodings) > 0:
            # Check shape (should be 128)
            shape = encodings[0].shape
            logger.info(f"Encoding vector dimension: {shape}")
            
            if shape == (128,):
                print("\n✅ DATA INTEGRITY CHECK: PASSED")
                print(f"   - Students Registered: {len(set(names))}")
                print(f"   - Total Samples: {len(encodings)}")
            else:
                logger.error(f"Invalid encoding dimension: {shape}")
        else:
            logger.warning("No encodings found in the file.")

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")

if __name__ == "__main__":
    verify_registration_data()
