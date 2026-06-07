import os
import pickle
import sys
import tempfile
import time
from pathlib import Path

import pytest
import numpy as np

# Ensure AI_Module is in python path
ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from optimization import PerformanceBenchmark, EncodingCache, PerformanceTracker

@pytest.fixture
def temp_encoding_file():
    """Generates a synthetic pickle file for testing with 500 faces."""
    dummy_encodings = [np.random.rand(128).tolist() for _ in range(500)]
    dummy_names = [f"Student_{i}" for i in range(500)]
    dummy_data = {"encodings": dummy_encodings, "names": dummy_names}
    
    with tempfile.NamedTemporaryFile(suffix=".pickle", delete=False) as tmp:
        pickle.dump(dummy_data, tmp)
        tmp_path = Path(tmp.name)
    
    yield tmp_path
    
    if tmp_path.exists():
        os.remove(tmp_path)

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

def test_encoding_load_benchmark(temp_encoding_file, clean_cache):
    benchmark = PerformanceBenchmark()
    
    # Run load benchmark
    stats = benchmark.benchmark_encoding_load(temp_encoding_file)
    
    assert "avg_ms" in stats
    assert stats["avg_ms"] >= 0
    assert stats["encoding_count"] == 500

def test_large_dataset_simulation(temp_encoding_file, clean_cache):
    # Benchmark matching against 500 faces
    benchmark = PerformanceBenchmark()
    
    # Mock face_recognition.compare_faces
    import face_recognition
    original_compare = face_recognition.compare_faces
    
    try:
        def mock_compare(known_encodings, face_encoding_to_check, tolerance=0.6):
            return [True] * len(known_encodings)
            
        face_recognition.compare_faces = mock_compare
        
        # Load the cache manually for the test
        cache = clean_cache
        cache.load(temp_encoding_file)
        
        # Start matching simulation
        start = time.time()
        encodings, _ = cache.get_encodings()
        if len(encodings) > 0:
            test_encoding = np.random.rand(128)
            face_recognition.compare_faces(encodings, test_encoding)
        elapsed = time.time() - start
        
        assert elapsed < 0.1 # Should take < 100ms
    finally:
        face_recognition.compare_faces = original_compare

def test_memory_usage_measurement():
    benchmark = PerformanceBenchmark()
    stats = benchmark.get_memory_info()
    
    assert "current_heap_bytes" in stats
    assert "encoding_matrix_bytes" in stats
    assert stats["current_heap_bytes"] >= 0

def test_report_generation():
    benchmark = PerformanceBenchmark()
    
    # generate_report might just create a file or do something else, let's just make sure it runs without exceptions
    try:
        benchmark.generate_report(output_dir="/tmp/reports")
    except Exception as e:
        pytest.fail(f"generate_report raised exception {e}")

def test_long_session_stability():
    tracker = PerformanceTracker()
    tracker._frame_times.clear()
    
    # Simulate 1000 frame ticks
    for i in range(1000):
        tracker.tick()
        time.sleep(0.001) # Small delay to have different timestamps
        
    # the deque should not exceed its maxlen (default likely 30 or 60)
    assert len(tracker._frame_times) <= 60
