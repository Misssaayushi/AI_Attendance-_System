import cv2
import face_recognition
import pickle
import os
from pathlib import Path
from ai_module.utils import get_logger
from ai_module.config import DATASET_DIR, ENCODINGS_DIR, ENCODING_FILE

def generate_encodings():
    logger = get_logger("EncodingGenerator")
    logger.info("Starting facial encoding generation...")

    # Data to be saved in the consolidated file
    known_encodings = []
    known_names = []

    # 1. Scan Dataset Directory
    student_folders = [f for f in DATASET_DIR.iterdir() if f.is_dir()]
    
    if not student_folders:
        logger.warning("No student folders found in dataset.")
        return

    for folder in student_folders:
        student_name = folder.name  # folder name is {id}_{name}
        logger.info(f"Processing student: {student_name}")
        
        student_encodings = []
        
        # 2. Process each image in student folder
        image_paths = list(folder.glob("*.jpg"))
        for img_path in image_paths:
            # Load image
            image = face_recognition.load_image_file(str(img_path))
            
            # Detect face and get encoding
            # We assume exactly one face per image because we validated during registration
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                encoding = encodings[0]
                student_encodings.append(encoding)
                known_encodings.append(encoding)
                known_names.append(student_name)
            else:
                logger.warning(f"No face found in {img_path.name}. Skipping.")

        # 3. Save individual student encoding file
        if student_encodings:
            individual_pkl = ENCODINGS_DIR / f"{student_name}.pkl"
            with open(individual_pkl, "wb") as f:
                pickle.dump(student_encodings, f)
            logger.info(f"Saved {len(student_encodings)} encodings to {individual_pkl.name}")

    # 4. Save Consolidated Encoding File (Used for recognition)
    if known_encodings:
        data = {"encodings": known_encodings, "names": known_names}
        with open(ENCODING_FILE, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Consolidated encoding file saved: {ENCODING_FILE}")
        print(f"\n✅ SUCCESS: Processed {len(student_folders)} students. Data ready for recognition.")

if __name__ == "__main__":
    generate_encodings()
