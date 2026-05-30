import os
import pickle
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest

# Ensure AI_Module is in python path
ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from optimization import EncodingCache, PerformanceTracker, FrameOptimizer, APIDispatcher

@pytest.fixture
def temp_encoding_file():
    """Generates a synthetic pickle file for testing."""
    dummy_encodings = [np.random.rand(128).tolist() for _ in range(3)]
    dummy_names = ["Student A", "Student B", "Student C"]
    dummy_data = {"encodings": dummy_encodings, "names": dummy_names}
    
    with tempfile.NamedTemporaryFile(suffix=".pickle", delete=False) as tmp:
        pickle.dump(dummy_data, tmp)
        tmp_path = Path(tmp.name)
    
    yield tmp_path, dummy_data
    
    if tmp_path.exists():
        os.remove(tmp_path)

@pytest.fixture
def dummy_frame():
    """Creates a random numpy array simulating a camera frame."""
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

@pytest.fixture
def clean_cache():
    """Returns a clean cache instance for testing."""
    cache = EncodingCache.get_instance()
    cache._encodings = np.empty((0, 128))
    cache._names = []
    cache._file_mtime = 0.0
    cache._loaded = False
    cache._load_time_ms = 0.0
    return cache

# --- EncodingCache Tests ---

def test_singleton_identity():
    cache1 = EncodingCache.get_instance()
    cache2 = EncodingCache.get_instance()
    assert cache1 is cache2

def test_load_valid_encoding(temp_encoding_file, clean_cache):
    tmp_path, dummy_data = temp_encoding_file
    cache = clean_cache
    cache.load(tmp_path)
    
    assert cache.is_loaded()
    encodings, names = cache.get_encodings()
    assert names == dummy_data["names"]
    assert encodings.shape == (3, 128)
    assert np.allclose(encodings[0], dummy_data["encodings"][0])

def test_load_missing_file(clean_cache):
    cache = clean_cache
    non_existent = Path("this_file_does_not_exist_12345.pickle")
    cache.load(non_existent)
    
    encodings, names = cache.get_encodings()
    assert len(names) == 0
    assert encodings.shape == (0, 128)
    assert not cache.is_loaded()

def test_load_corrupted_file(temp_encoding_file, clean_cache):
    tmp_path, _ = temp_encoding_file
    with open(tmp_path, "wb") as f:
        f.write(b"corrupted data")
        
    cache = clean_cache
    cache.load(tmp_path)
    
    encodings, names = cache.get_encodings()
    assert len(names) == 0
    assert not cache.is_loaded()

def test_reload_on_file_change(temp_encoding_file, clean_cache):
    tmp_path, dummy_data = temp_encoding_file
    cache = clean_cache
    cache.load(tmp_path)
    
    # Force check bypass
    cache._last_check_time = 0.0
    cache.encoding_file = tmp_path
    
    time.sleep(1.1)
    dummy_data["encodings"].append(np.random.rand(128).tolist())
    dummy_data["names"].append("Student D")
    with open(tmp_path, "wb") as f:
        pickle.dump(dummy_data, f)
        
    assert cache.reload_if_changed() is True
    _, names = cache.get_encodings()
    assert len(names) == 4
    assert names[-1] == "Student D"

def test_no_reload_when_unchanged(temp_encoding_file, clean_cache):
    tmp_path, _ = temp_encoding_file
    cache = clean_cache
    cache.load(tmp_path)
    
    cache._last_check_time = 0.0
    cache.encoding_file = tmp_path
    assert cache.reload_if_changed() is False

def test_numpy_matrix_shape(temp_encoding_file, clean_cache):
    tmp_path, dummy_data = temp_encoding_file
    cache = clean_cache
    cache.load(tmp_path)
    
    encodings, _ = cache.get_encodings()
    assert encodings.shape == (len(dummy_data["names"]), 128)

def test_get_stats_returns_expected_keys(temp_encoding_file, clean_cache):
    tmp_path, _ = temp_encoding_file
    cache = clean_cache
    cache.load(tmp_path)
    
    stats = cache.get_stats()
    assert "encoding_count" in stats
    assert "memory_estimate_bytes" in stats
    assert "load_time_ms" in stats

# --- PerformanceTracker Tests ---

def test_fps_calculation():
    tracker = PerformanceTracker()
    tracker._frame_times.clear()
    
    now = time.time()
    for i in range(10):
        tracker._frame_times.append(0.05) # simulate exactly 0.05 interval
        
    fps = tracker.get_fps()
    assert 18 <= fps <= 22

def test_rolling_average():
    tracker = PerformanceTracker()
    tracker._frame_times.clear()
    
    # 5 fast frames, 5 slow frames
    for i in range(10):
        tracker._frame_times.append(0.1) # 10 FPS
        
    avg_fps = tracker.get_avg_fps()
    assert avg_fps > 0

@patch("optimization.TARGET_FPS", 15)
@patch("optimization.ENABLE_ADAPTIVE_INTERVAL", True)
def test_adaptive_interval_decrease():
    tracker = PerformanceTracker()
    tracker._current_interval = 10
    
    # Simulate high FPS (fast processing, e.g. 30 FPS)
    for i in range(30):
        tracker._frame_times.append(1.0/30.0)
        
    interval = tracker.get_recommended_interval()
    assert interval < 10

@patch("optimization.TARGET_FPS", 15)
@patch("optimization.ENABLE_ADAPTIVE_INTERVAL", True)
def test_adaptive_interval_increase():
    tracker = PerformanceTracker()
    tracker._current_interval = 10
    
    # Simulate low FPS (e.g. 5 FPS)
    for i in range(30):
        tracker._frame_times.append(1.0/5.0)
        
    interval = tracker.get_recommended_interval()
    assert interval > 10

@patch("optimization.TARGET_FPS", 15)
@patch("optimization.ENABLE_ADAPTIVE_INTERVAL", True)
@patch("optimization.MAX_PROCESS_INTERVAL", 60)
@patch("optimization.MIN_PROCESS_INTERVAL", 1)
def test_adaptive_interval_bounds():
    tracker = PerformanceTracker()
    
    # Force a very low FPS
    for i in range(30):
        tracker._frame_times.append(10.0)
    tracker._current_interval = 60
    interval_high = tracker.get_recommended_interval()
    assert interval_high <= 60
    
    # Force a very high FPS
    for i in range(30):
        tracker._frame_times.append(0.001)
    tracker._current_interval = 1
    interval_low = tracker.get_recommended_interval()
    assert interval_low >= 1

def test_status_string_format():
    tracker = PerformanceTracker()
    tracker.tick()
    time.sleep(0.01)
    tracker.tick()
    status = tracker.get_status_string()
    assert "FPS:" in status

# --- FrameOptimizer Tests ---

def test_crop_within_bounds(dummy_frame):
    optimizer = FrameOptimizer()
    box = (200, 400, 300, 200) # top, right, bottom, left
    
    cropped = optimizer.crop_face_region(dummy_frame, box, padding=20)
    assert cropped is not None
    assert cropped.shape[0] > 0 and cropped.shape[1] > 0

def test_crop_at_edge(dummy_frame):
    optimizer = FrameOptimizer()
    box = (0, 200, 100, 0) # top, right, bottom, left
    
    cropped = optimizer.crop_face_region(dummy_frame, box, padding=50)
    assert cropped is not None
    assert cropped.shape[0] > 0 and cropped.shape[1] > 0

def test_prepare_frame_returns_rgb(dummy_frame):
    optimizer = FrameOptimizer()
    dummy_frame[0, 0] = [255, 0, 0] # Blue in BGR
    
    rgb_frame = optimizer.prepare_frame(dummy_frame)
    assert np.array_equal(rgb_frame[0, 0], [0, 0, 255]) # Should be Red in RGB

def test_generate_encoding_returns_128d(dummy_frame):
    optimizer = FrameOptimizer()
    # Mocking face_recognition.face_encodings to return dummy
    import face_recognition
    original = face_recognition.face_encodings
    try:
        face_recognition.face_encodings = lambda x, y=None: [np.zeros(128)]
        encoding, success = optimizer.generate_encoding(dummy_frame, (10, 50, 50, 10))
        assert encoding is not None
        assert encoding.shape == (128,)
    finally:
        face_recognition.face_encodings = original

# --- APIDispatcher Tests ---
class DummyAPI:
    def __init__(self, delay=0):
        self.delay = delay
    def send_verified_attendance(self, sid, name, conf):
        time.sleep(self.delay)
        return {"success": True}

@patch("optimization.API_DISPATCH_ASYNC", True)
def test_dispatch_does_not_block():
    dispatcher = APIDispatcher()
    api = DummyAPI(delay=0.5)
    
    start = time.time()
    dispatcher.dispatch(api, "S123", "Alice", 0.99)
    elapsed = time.time() - start
    
    assert elapsed < 0.1 # Should return immediately
    time.sleep(0.6) # Let thread finish

@patch("optimization.API_DISPATCH_ASYNC", True)
def test_result_retrieval():
    dispatcher = APIDispatcher()
    api = DummyAPI(delay=0.1)
    
    dispatcher.dispatch(api, "S456", "Bob", 0.95)
    time.sleep(0.3)
    
    completed, result = dispatcher.get_result("S456")
    assert completed is True
    assert result is not None
    assert result["success"] is True

@patch("optimization.API_DISPATCH_ASYNC", True)
def test_duplicate_prevention():
    dispatcher = APIDispatcher()
    api = DummyAPI(delay=0.5)
    
    dispatcher.dispatch(api, "S789", "Charlie", 0.99)
    
    # Wait slightly to ensure thread started and added to pending
    time.sleep(0.1)
    assert dispatcher.is_pending("S789") is True
    
    time.sleep(0.6)

def test_collect_expired():
    dispatcher = APIDispatcher()
    dispatcher._results["S111"] = ({"success": True}, time.time() - 400)
    
    removed = dispatcher.collect_expired(max_age_seconds=300)
    assert removed == 1
    assert "S111" not in dispatcher._results
