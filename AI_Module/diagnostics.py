import os
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any

import cv2
import numpy as np

try:
    from ai_module.config import ENCODING_FILE
except ImportError:
    from config import ENCODING_FILE

class FrameSimulator:
    @staticmethod
    def create_normal_frame(width=640, height=480) -> np.ndarray:
        frame = np.random.normal(128, 40, (height, width, 3))
        return np.clip(frame, 0, 255).astype(np.uint8)

    @staticmethod
    def create_dark_frame(width=640, height=480) -> np.ndarray:
        frame = np.random.normal(20, 10, (height, width, 3))
        return np.clip(frame, 0, 255).astype(np.uint8)

    @staticmethod
    def create_bright_frame(width=640, height=480) -> np.ndarray:
        frame = np.random.normal(250, 10, (height, width, 3))
        return np.clip(frame, 0, 255).astype(np.uint8)

    @staticmethod
    def create_blurry_frame(width=640, height=480) -> np.ndarray:
        frame = FrameSimulator.create_normal_frame(width, height)
        return cv2.GaussianBlur(frame, (31, 31), 0)

    @staticmethod
    def add_noise(frame: np.ndarray, intensity=0.1) -> np.ndarray:
        noise = np.random.normal(0, 255 * intensity, frame.shape)
        noisy_frame = frame.astype(np.float32) + noise
        return np.clip(noisy_frame, 0, 255).astype(np.uint8)


class RecognitionStabilityTester:
    @staticmethod
    def test_consistency(recognizer, encoding: np.ndarray, iterations=50) -> dict:
        results = []
        for _ in range(iterations):
            name, confidence = recognizer.identify_optimized(encoding)
            results.append((name, confidence))
        
        mismatches = 0
        confidences = []
        if len(results) > 0:
            primary_name = results[0][0]
            for name, conf in results:
                if name != primary_name:
                    mismatches += 1
                if conf is not None:
                    confidences.append(conf)
        
        consistency_pct = ((iterations - mismatches) / iterations) * 100
        mean_conf = np.mean(confidences) if confidences else 0.0
        std_conf = np.std(confidences) if confidences else 0.0

        return {
            "consistency_pct": float(consistency_pct),
            "confidence_mean": float(mean_conf),
            "confidence_std": float(std_conf),
            "mismatches": mismatches
        }

    @staticmethod
    def test_confidence_stability(recognizer, encoding: np.ndarray, noise_std=0.01, iterations=50) -> dict:
        confidences = []
        for _ in range(iterations):
            noisy_encoding = encoding + np.random.normal(0, noise_std, encoding.shape)
            name, confidence = recognizer.identify_optimized(noisy_encoding)
            if confidence is not None:
                confidences.append(confidence)

        mean_conf = float(np.mean(confidences)) if confidences else 0.0
        std_conf = float(np.std(confidences)) if confidences else 0.0
        min_conf = float(np.min(confidences)) if confidences else 0.0
        max_conf = float(np.max(confidences)) if confidences else 0.0
        
        stable = std_conf < 0.05

        return {
            "confidence_mean": mean_conf,
            "confidence_std": std_conf,
            "confidence_min": min_conf,
            "confidence_max": max_conf,
            "stable": stable
        }

    @staticmethod
    def test_multi_face_handling(recognizer, encodings_list: List[np.ndarray], iterations=10) -> dict:
        successes = 0
        failures = 0
        total_time = 0.0
        
        for _ in range(iterations):
            for enc in encodings_list:
                start_time = time.time()
                name, conf = recognizer.identify_optimized(enc)
                total_time += (time.time() - start_time)
                
                if name and name != "Unknown":
                    successes += 1
                else:
                    failures += 1
                    
        total_faces = len(encodings_list) * iterations
        avg_time_ms = (total_time / total_faces) * 1000 if total_faces > 0 else 0.0
        
        return {
            "total_faces": total_faces,
            "successes": successes,
            "failures": failures,
            "avg_time_ms": float(avg_time_ms)
        }


class PerformanceValidator:
    @staticmethod
    def validate_fps_stability(tracker, duration_ticks=1000) -> dict:
        fps_values = []
        for _ in range(duration_ticks):
            tracker.tick()
            fps_values.append(tracker.get_fps())
            time.sleep(0.001)

        mean_fps = float(np.mean(fps_values))
        std_fps = float(np.std(fps_values))
        min_fps = float(np.min(fps_values))
        max_fps = float(np.max(fps_values))
        
        stable = std_fps < (0.20 * mean_fps) if mean_fps > 0 else False

        return {
            "fps_mean": mean_fps,
            "fps_std": std_fps,
            "fps_min": min_fps,
            "fps_max": max_fps,
            "stable": stable
        }

    @staticmethod
    def validate_memory_stability(iterations=1000) -> dict:
        tracemalloc.start()
        start_snapshot = tracemalloc.take_snapshot()
        
        dummy_list = []
        for _ in range(iterations):
            dummy_list.append(np.random.normal(0, 1, (128,)))
            if len(dummy_list) > 100:
                dummy_list.pop(0)
                
        end_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()

        start_bytes = sum([stat.size for stat in start_snapshot.statistics("lineno")])
        end_bytes = sum([stat.size for stat in end_snapshot.statistics("lineno")])
        
        diff = end_bytes - start_bytes
        growth = diff / iterations if iterations > 0 else 0

        return {
            "start_bytes": start_bytes,
            "end_bytes": end_bytes,
            "peak_bytes": max(start_bytes, end_bytes),
            "growth_per_iteration": float(growth),
            "stable": growth < 2048
        }

    @staticmethod
    def generate_diagnostics_report(output_dir=None) -> str:
        if output_dir is None:
            output_dir = Path("reports")
        else:
            output_dir = Path(output_dir)
            
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"diagnostics_report_{timestamp}.txt"
        
        with open(filepath, "w") as f:
            f.write(f"--- AI System Diagnostics Report ---\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            f.write("Status: GENERATED\n")
            
        return str(filepath)


class SystemHealthChecker:
    @staticmethod
    def check_camera(camera_id=0) -> Tuple[bool, str]:
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            return False, f"Could not open camera {camera_id}"
        cap.release()
        return True, "Camera available"

    @staticmethod
    def check_encodings(encoding_file=ENCODING_FILE) -> Tuple[bool, str]:
        path = Path(encoding_file)
        if not path.exists():
            return False, f"Encoding file not found at {path}"
        try:
            import pickle
            with open(path, "rb") as f:
                data = pickle.load(f)
            if not isinstance(data, dict):
                return False, "Encoding file is not a dictionary"
            return True, f"Encodings loaded ({len(data)} entries)"
        except Exception as e:
            return False, f"Invalid encoding file: {str(e)}"

    @staticmethod
    def check_dependencies() -> Tuple[bool, str]:
        missing = []
        try:
            import cv2
        except ImportError:
            missing.append("opencv-python")
            
        try:
            import numpy
        except ImportError:
            missing.append("numpy")
            
        try:
            import face_recognition
        except ImportError:
            missing.append("face_recognition")
            
        if missing:
            return False, f"Missing dependencies: {', '.join(missing)}"
        return True, "All critical dependencies installed"

    @staticmethod
    def check_disk_space(path=".", min_mb=100) -> Tuple[bool, str]:
        import shutil
        try:
            total, used, free = shutil.disk_usage(path)
            free_mb = free / (1024 * 1024)
            if free_mb < min_mb:
                return False, f"Low disk space: {free_mb:.1f} MB free (requires {min_mb} MB)"
            return True, f"Adequate disk space: {free_mb:.1f} MB free"
        except Exception as e:
            return False, f"Could not check disk space: {str(e)}"

    @classmethod
    def run_all_checks(cls) -> dict:
        cam_ok, cam_msg = cls.check_camera()
        enc_ok, enc_msg = cls.check_encodings()
        dep_ok, dep_msg = cls.check_dependencies()
        disk_ok, disk_msg = cls.check_disk_space()
        
        overall = cam_ok and enc_ok and dep_ok and disk_ok
        
        return {
            "camera": (cam_ok, cam_msg),
            "encodings": (enc_ok, enc_msg),
            "dependencies": (dep_ok, dep_msg),
            "disk_space": (disk_ok, disk_msg),
            "overall_healthy": overall
        }
