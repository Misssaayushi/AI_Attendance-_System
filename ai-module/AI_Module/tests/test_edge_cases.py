import os
import sys
import tempfile
import time
import pickle
import threading
import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from optimization import EncodingCache, APIDispatcher
from utils import FaceDetector, FaceRecognizer, EncodingManager, AttendanceManager
from config import UNKNOWN_LABEL

@pytest.fixture
def empty_encoding_file():
    with tempfile.NamedTemporaryFile(suffix=".pickle", delete=False) as f:
        pickle.dump({"encodings": [], "names": []}, f)
        temp_path = f.name
    yield temp_path
    os.remove(temp_path)

@pytest.fixture
def enc_mgr(empty_encoding_file):
    return EncodingManager(empty_encoding_file)

# ==============================================================================
# Part A: Encoding Edge Cases
# ==============================================================================

def test_empty_encoding_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "empty_encodings.pickle")
        with open(file_path, "wb") as f:
            pickle.dump({"encodings": [], "names": []}, f)
            
        cache = EncodingCache.get_instance()
        cache.load(file_path)
        
        assert cache.is_loaded() is True
        encodings, names = cache.get_encodings()
        assert encodings.shape == (0, 128)
        assert len(names) == 0
        
        recognizer = FaceRecognizer(EncodingManager(file_path))
        
        dummy_encoding = np.zeros(128)
        name, conf = recognizer.identify_optimized(dummy_encoding)
        assert name == UNKNOWN_LABEL
        assert conf == 0.0

def test_mismatched_encoding_names_count():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "mismatched.pickle")
        with open(file_path, "wb") as f:
            pickle.dump({"encodings": [np.zeros(128)] * 3, "names": ["A", "B"]}, f)
            
        cache = EncodingCache.get_instance()
        cache.load(file_path)
        
        assert cache.is_loaded() is False

def test_corrupted_pickle_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "corrupted.pickle")
        with open(file_path, "wb") as f:
            f.write(b"random garbage bytes that are not a pickle")
            
        cache = EncodingCache.get_instance()
        cache.load(file_path)
        
        assert cache.is_loaded() is False

def test_nan_encoding_handling(enc_mgr):
    recognizer = FaceRecognizer(enc_mgr)
    cache = EncodingCache.get_instance()
    cache._encodings = np.array([np.zeros(128)])
    cache._names = ["Test"]
    
    nan_encoding = np.array([float('nan')] * 128)
    name, conf = recognizer.identify_optimized(nan_encoding)
    assert name == UNKNOWN_LABEL
    assert conf == 0.0

def test_single_registered_face():
    with tempfile.NamedTemporaryFile(suffix=".pickle", delete=False) as f:
        pickle.dump({"encodings": [np.ones(128)], "names": ["SingleStudent"]}, f)
        temp_path = f.name
    
    enc_mgr = EncodingManager(temp_path)
    recognizer = FaceRecognizer(enc_mgr)
    name, conf = recognizer.identify_optimized(np.ones(128))
    assert name == "SingleStudent"
    assert conf > 0.0
    os.remove(temp_path)

# ==============================================================================
# Part B: Frame Edge Cases
# ==============================================================================

def test_zero_size_frame():
    detector = FaceDetector()
    frame = np.empty((0, 0, 3), dtype=np.uint8)
    locations = detector.detect_faces(frame)
    assert locations == []

def test_none_frame_detection():
    detector = FaceDetector()
    locations = detector.detect_faces(None)
    assert locations == []

def test_very_large_frame():
    detector = FaceDetector()
    frame = np.zeros((2000, 2000, 3), dtype=np.uint8)
    locations = detector.detect_faces(frame)
    assert isinstance(locations, list)

def test_grayscale_frame():
    detector = FaceDetector()
    frame = np.zeros((480, 640), dtype=np.uint8)
    locations = detector.detect_faces(frame)
    assert locations == []

# ==============================================================================
# Part C: Recognition Behavior Edge Cases
# ==============================================================================

def test_zero_face_locations_processing(enc_mgr):
    try:
        from optimization import FrameOptimizer
        optimizer = FrameOptimizer()
        encodings = optimizer.process_faces(np.zeros((100, 100, 3), dtype=np.uint8), [])
        assert encodings == []
    except Exception as e:
        pytest.fail(f"Exception raised: {e}")

def test_confidence_bounds(enc_mgr):
    recognizer = FaceRecognizer(enc_mgr)
    cache = EncodingCache.get_instance()
    cache._encodings = np.array([np.zeros(128)])
    cache._names = ["Test"]
    
    name, conf = recognizer.identify_optimized(np.zeros(128))
    assert conf <= 99.0

def test_confidence_at_tolerance_boundary(enc_mgr):
    recognizer = FaceRecognizer(enc_mgr)
    cache = EncodingCache.get_instance()
    cache._encodings = np.array([np.zeros(128)])
    cache._names = ["Test"]
    
    with patch("face_recognition.face_distance", return_value=np.array([0.6])):
        name, conf = recognizer.identify_optimized(np.zeros(128))
        if name != UNKNOWN_LABEL:
            assert conf == 75.0

def test_unknown_flood_no_memory_growth():
    manager = AttendanceManager()
    manager.unknown_streak = 0
    for _ in range(200):
        manager.verify_attendance("unknown_id", UNKNOWN_LABEL, 0.0)
        
    assert manager.unknown_streak == 200
    assert len(manager.verified_cache) == 0

# ==============================================================================
# Part D: Concurrency Edge Cases
# ==============================================================================

def test_concurrent_api_dispatches():
    dispatcher = APIDispatcher()
    api_service = MagicMock()
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=dispatcher.dispatch, args=(api_service, f"Student_{i}", f"Student_{i}", 0.9))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    dispatcher.cleanup()
    assert len(dispatcher._pending) == 0

def test_cooldown_boundary_precision():
    manager = AttendanceManager(cooldown_minutes=0.05, stability_frames=1) # 3 seconds
    
    # First verification
    manager.verify_attendance("BoundaryStudent", "BoundaryStudent", 95.0)
    
    # Immediately after, should be on cooldown
    assert manager.is_on_cooldown("BoundaryStudent") is True
    
    # Move time forward by 3.1 seconds
    last_verified = manager.verified_cache["BoundaryStudent"]
    with patch('utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = last_verified + datetime.timedelta(seconds=3.1)
        assert manager.is_on_cooldown("BoundaryStudent") is False
