import os
import pickle
import threading
import time
import sys
from pathlib import Path
import numpy as np
import platform
import multiprocessing
import tracemalloc

# Start memory tracing early
if not tracemalloc.is_tracing():
    tracemalloc.start()
from typing import Optional

# Optional heavy deps:
# - Keep imports lazy so importing this module doesn't hard-fail in environments
#   where OpenCV / face_recognition aren't installed (e.g. running only cache/tests).
# - When FrameOptimizer methods are used, we validate availability and raise a clear error.
try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - depends on environment
    cv2 = None  # type: ignore[assignment]

try:
    import face_recognition  # type: ignore
except Exception:  # pragma: no cover - depends on environment
    face_recognition = None  # type: ignore[assignment]

from collections import deque

# Import config and logger with fallbacks for package/non-package execution
try:
    from ai_module.config import (
        ENCODING_FILE,
        ENCODING_RELOAD_CHECK_SECONDS,
        TARGET_FPS,
        MIN_PROCESS_INTERVAL,
        MAX_PROCESS_INTERVAL,
        ENABLE_ADAPTIVE_INTERVAL,
        PERF_TRACKER_WINDOW,
        RECOGNITION_PROCESS_INTERVAL,
        FACE_CROP_PADDING,
        API_DISPATCH_ASYNC,
        API_FEEDBACK_DISPLAY_SECONDS,
        API_FEEDBACK_CLEANUP_INTERVAL,
        BENCHMARK_REPORT_DIR,
    )
    from ai_module.utils import get_logger
except ImportError:
    try:
        from config import (
            ENCODING_FILE,
            ENCODING_RELOAD_CHECK_SECONDS,
            TARGET_FPS,
            MIN_PROCESS_INTERVAL,
            MAX_PROCESS_INTERVAL,
            ENABLE_ADAPTIVE_INTERVAL,
            PERF_TRACKER_WINDOW,
            RECOGNITION_PROCESS_INTERVAL,
            FACE_CROP_PADDING,
            API_DISPATCH_ASYNC,
            API_FEEDBACK_DISPLAY_SECONDS,
            API_FEEDBACK_CLEANUP_INTERVAL,
            BENCHMARK_REPORT_DIR,
        )
        from utils import get_logger
    except ImportError:
        # Fallback path inclusion if executed directly
        sys.path.append(str(Path(__file__).resolve().parent))
        from config import (
            ENCODING_FILE,
            ENCODING_RELOAD_CHECK_SECONDS,
            TARGET_FPS,
            MIN_PROCESS_INTERVAL,
            MAX_PROCESS_INTERVAL,
            ENABLE_ADAPTIVE_INTERVAL,
            PERF_TRACKER_WINDOW,
            RECOGNITION_PROCESS_INTERVAL,
            FACE_CROP_PADDING,
            API_DISPATCH_ASYNC,
            API_FEEDBACK_DISPLAY_SECONDS,
            API_FEEDBACK_CLEANUP_INTERVAL,
            BENCHMARK_REPORT_DIR,
        )
        from utils import get_logger

logger = get_logger("EncodingCache")


def _require_dependency(module, name: str, install_hint: str):
    if module is None:
        raise ImportError(
            f"Missing optional dependency '{name}'. {install_hint} "
            f"(If you're using the repo venv: ensure VS Code interpreter points to "
            f"'ai-module/AI_Module/venv/bin/python' or run via 'source venv/bin/activate'.)"
        )
    return module


class EncodingCache:
    """
    Thread-safe, hot-reloading Singleton cache for face encodings.
    Converts list of encodings to a single NumPy matrix for fast, vectorized distance calculation.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Prevent direct initialization or re-initialization
        if EncodingCache._instance is not None:
            raise RuntimeError("Use get_instance() instead of direct instantiation")
        
        self.encoding_file = Path(ENCODING_FILE)
        self._encodings = np.empty((0, 128))
        self._names = []
        self._file_mtime = 0.0
        self._last_check_time = 0.0
        self._load_time_ms = 0.0
        self._last_reload_time = 0.0
        self._loaded = False
        self._access_lock = threading.Lock()
        
        # Eager load on creation
        self.load(self.encoding_file)

    @classmethod
    def get_instance(cls):
        """
        Returns the single shared thread-safe instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load(self, path):
        """
        Loads the consolidate encoding pickle file and converts lists to np.ndarray.
        Thread-safe.
        """
        path = Path(path)
        start_time = time.perf_counter()
        
        if not path.exists():
            logger.warning(f"Encoding file {path} not found. Recognition will not work until faces are encoded.")
            with self._access_lock:
                self._encodings = np.empty((0, 128))
                self._names = []
                self._file_mtime = 0.0
                self._loaded = False
                self._load_time_ms = (time.perf_counter() - start_time) * 1000.0
                self._last_reload_time = time.time()
            return

        try:
            mtime = os.path.getmtime(path)
            with open(path, "rb") as f:
                data = pickle.load(f)
            
            # Validate structure
            if not isinstance(data, dict) or "encodings" not in data or "names" not in data:
                raise ValueError("Invalid pickle structure. Must contain 'encodings' and 'names' keys.")
            
            encodings_list = data.get("encodings", [])
            names_list = data.get("names", [])
            
            if len(encodings_list) != len(names_list):
                raise ValueError(f"Mismatch between encodings count ({len(encodings_list)}) and names count ({len(names_list)})")

            if encodings_list:
                encodings_matrix = np.array(encodings_list, dtype=np.float64)
                # Verify shape is N x 128
                if len(encodings_matrix.shape) != 2 or encodings_matrix.shape[1] != 128:
                    raise ValueError(f"Encodings must be 128-dimensional vectors. Got shape {encodings_matrix.shape}")
            else:
                encodings_matrix = np.empty((0, 128))

            with self._access_lock:
                self._encodings = encodings_matrix
                self._names = names_list
                self._file_mtime = mtime
                self._loaded = True
                self._load_time_ms = (time.perf_counter() - start_time) * 1000.0
                self._last_reload_time = time.time()
                self._last_check_time = time.time()
            
            logger.info(f"Successfully cached {len(names_list)} face encodings in {self._load_time_ms:.2f} ms.")

        except Exception as e:
            logger.error(f"Failed to load encodings: {str(e)}")
            with self._access_lock:
                self._encodings = np.empty((0, 128))
                self._names = []
                self._file_mtime = 0.0
                self._loaded = False
                self._load_time_ms = (time.perf_counter() - start_time) * 1000.0
                self._last_reload_time = time.time()

    def reload_if_changed(self):
        """
        Compares stored timestamp with current timestamp and reloads if the file has changed.
        Thread-safe.
        """
        now = time.time()
        # Throttling to prevent excessive disk mtime checks under hot loops
        if now - self._last_check_time < ENCODING_RELOAD_CHECK_SECONDS:
            return False

        self._last_check_time = now
        
        if not self.encoding_file.exists():
            if self._loaded:
                # File was deleted, reset cache
                logger.warning(f"Encoding file {self.encoding_file} was deleted. Resetting cache.")
                self.load(self.encoding_file)
                return True
            return False

        try:
            current_mtime = os.path.getmtime(self.encoding_file)
            if current_mtime > self._file_mtime:
                logger.info(f"Encoding file change detected (mtime changed). Reloading cache...")
                self.load(self.encoding_file)
                return True
        except Exception as e:
            logger.error(f"Error checking file modification time: {str(e)}")
        
        return False

    def get_encodings(self):
        """
        Returns a tuple of (encodings_matrix, names_list).
        Thread-safe.
        """
        with self._access_lock:
            return self._encodings, self._names

    def is_loaded(self):
        """
        Returns whether encodings have been successfully loaded.
        Thread-safe.
        """
        with self._access_lock:
            return self._loaded

    def get_stats(self):
        """
        Returns a dictionary of cache statistics.
        Thread-safe.
        """
        with self._access_lock:
            count = len(self._names)
            # Estimate memory based on float64 numpy array (8 bytes per value) and name string overhead
            numpy_mem = self._encodings.nbytes
            names_mem = sum(len(name.encode('utf-8')) + 49 for name in self._names) # 49 bytes base python string overhead
            mem_estimate_bytes = numpy_mem + names_mem
            
            file_size_bytes = 0
            if self.encoding_file.exists():
                try:
                    file_size_bytes = os.path.getsize(self.encoding_file)
                except Exception:
                    pass

            return {
                "encoding_count": count,
                "file_size_bytes": file_size_bytes,
                "load_time_ms": self._load_time_ms,
                "memory_estimate_bytes": mem_estimate_bytes,
                "last_reload_timestamp": self._last_reload_time,
                "file_mtime": self._file_mtime
            }


class PerformanceTracker:
    """
    Measures real-time FPS, frame processing time, and provides adaptive processing interval recommendations.
    Thread-safe.
    """
    def __init__(self):
        self._frame_times = deque(maxlen=PERF_TRACKER_WINDOW)
        self._last_tick = None
        self._last_frame_duration = 0.0
        self._current_interval = RECOGNITION_PROCESS_INTERVAL
        self._lock = threading.Lock()

    def tick(self):
        """
        Record a new frame arrival time. Calculates elapsed time since the last tick
        and appends it to the rolling window.
        """
        now = time.perf_counter()
        with self._lock:
            if self._last_tick is not None:
                elapsed = now - self._last_tick
                # Prevent division by zero / negative elapsed time in case of clock shifts
                if elapsed > 0:
                    self._frame_times.append(elapsed)
            self._last_tick = now

    def record_processing_time(self, duration_ms):
        """
        Record the active processing duration (in milliseconds) of the current frame's
        AI operations (detection and/or recognition).
        """
        with self._lock:
            self._last_frame_duration = duration_ms

    def get_fps(self):
        """
        Returns the instantaneous FPS (1 / last frame interval).
        Returns 0.0 if not enough data.
        """
        with self._lock:
            if not self._frame_times:
                return 0.0
            last_duration = self._frame_times[-1]
            return 1.0 / last_duration if last_duration > 0 else 0.0

    def get_avg_fps(self):
        """
        Returns the rolling average FPS over the configured tracker window.
        Returns 0.0 if not enough data.
        """
        with self._lock:
            if not self._frame_times:
                return 0.0
            avg_duration = sum(self._frame_times) / len(self._frame_times)
            return 1.0 / avg_duration if avg_duration > 0 else 0.0

    def get_frame_time_ms(self):
        """
        Returns the processing time of the last active frame in milliseconds.
        """
        with self._lock:
            return self._last_frame_duration

    def get_recommended_interval(self):
        """
        Calculates and returns the recommended processing interval (frame skip count).
        Adapts dynamically based on avg_fps to target TARGET_FPS.
        """
        if not ENABLE_ADAPTIVE_INTERVAL:
            return RECOGNITION_PROCESS_INTERVAL

        with self._lock:
            # Need at least a few frames to make an informed recommendation
            if len(self._frame_times) < 5:
                return self._current_interval

            avg_fps = 1.0 / (sum(self._frame_times) / len(self._frame_times))

            if avg_fps > TARGET_FPS * 1.2:
                # High performance: reduce interval to process more frequently (more accuracy)
                self._current_interval = max(MIN_PROCESS_INTERVAL, self._current_interval - 1)
            elif avg_fps < TARGET_FPS * 0.8:
                # Low performance: increase interval to skip more frames (prevents lag)
                self._current_interval = min(MAX_PROCESS_INTERVAL, self._current_interval + 1)
            
            return self._current_interval

    def get_status_string(self):
        """
        Returns a formatted performance diagnostic string.
        """
        avg_fps = self.get_avg_fps()
        inst_fps = self.get_fps()
        interval = self.get_recommended_interval()
        frame_time = self.get_frame_time_ms()
        return f"FPS: {inst_fps:.1f} | Avg: {avg_fps:.1f} | Interval: {interval} | FrameTime: {frame_time:.1f}ms"


class FrameOptimizer:
    """
    Implements the crop-then-encode strategy and memory-efficient frame preprocessing.
    Reduces compute time of face_recognition.face_encodings by running on small cropped regions.
    """
    def __init__(self):
        self._padding = FACE_CROP_PADDING

    def prepare_frame(self, bgr_frame):
        """
        Converts a BGR frame from OpenCV to RGB once.
        Returns the converted RGB frame.
        """
        if bgr_frame is None:
            return None
        _cv2 = _require_dependency(cv2, "cv2", "Install with `pip install opencv-python`.")
        return _cv2.cvtColor(bgr_frame, _cv2.COLOR_BGR2RGB)

    def crop_face_region(self, rgb_frame, face_location, padding=None):
        """
        Extracts the face region with configurable padding around the bounding box,
        clamping coordinates to frame boundaries to prevent out-of-bounds errors.
        """
        if rgb_frame is None or face_location is None:
            return None

        if padding is None:
            padding = self._padding

        h, w, _ = rgb_frame.shape
        top, right, bottom, left = face_location

        # Apply padding and clamp to image boundaries
        crop_top = max(0, top - padding)
        crop_left = max(0, left - padding)
        crop_bottom = min(h, bottom + padding)
        crop_right = min(w, right + padding)

        # Extract the cropped region
        return rgb_frame[crop_top:crop_bottom, crop_left:crop_right]

    def generate_encoding(self, rgb_frame, face_location):
        """
        Crops the face region, then calls face_recognition.face_encodings on the smaller crop.
        Falls back to full-frame encoding if the crop fails or produces no encoding.
        Returns (encoding, success) tuple.
        """
        if rgb_frame is None or face_location is None:
            return None, False

        # 1. Attempt crop-then-encode
        cropped_region = self.crop_face_region(rgb_frame, face_location)
        if cropped_region is not None and cropped_region.size > 0:
            try:
                # When passing a crop, the location of the face relative to the crop is the entire crop.
                # So we do not pass face_locations, which lets face_recognition run its detector
                # internally on the smaller cropped image, finding the face very quickly.
                _fr = _require_dependency(
                    face_recognition,
                    "face_recognition",
                    "Install with `pip install face_recognition` (requires dlib build deps).",
                )
                encodings = _fr.face_encodings(cropped_region)
                if encodings:
                    return encodings[0], True
            except Exception as e:
                logger.warning(f"Failed to generate encoding on crop: {str(e)}. Falling back to full frame.")

        # 2. Fallback to full frame encoding
        try:
            _fr = _require_dependency(
                face_recognition,
                "face_recognition",
                "Install with `pip install face_recognition` (requires dlib build deps).",
            )
            encodings = _fr.face_encodings(rgb_frame, [face_location])
            if encodings:
                return encodings[0], False
        except Exception as e:
            logger.error(f"Failed to generate encoding on full frame: {str(e)}")

        return None, False

    def process_faces(self, rgb_frame, face_locations):
        """
        Processes multiple face locations efficiently by cropping and encoding each one.
        Returns a list of (encoding, face_location) tuples.
        """
        results = []
        if rgb_frame is None or not face_locations:
            return results

        for loc in face_locations:
            encoding, success = self.generate_encoding(rgb_frame, loc)
            if encoding is not None:
                results.append((encoding, loc))
                
        return results


class APIDispatcher:
    """
    Wraps attendance API calls in a background thread to prevent blocking the webcam render loop.
    Supports thread-safe status tracking, duplicate prevention, and results caching.
    """
    def __init__(self):
        self._results = {}       # student_id -> (AttendanceAPIResponse, timestamp)
        self._pending = set()    # student_ids in-flight
        self._lock = threading.Lock()

    def dispatch(self, api_service, student_id, name, confidence):
        """
        Spawns a background thread to submit attendance verification non-blockingly,
        unless API_DISPATCH_ASYNC is disabled (falls back to synchronous execution).
        """
        if not api_service or not student_id:
            return

        with self._lock:
            # Prevent duplicate pending requests for the same student
            if student_id in self._pending:
                return

            self._pending.add(student_id)

        # Synchronous fallback if configured
        if not API_DISPATCH_ASYNC:
            try:
                response = api_service.send_verified_attendance(student_id, name, confidence)
                with self._lock:
                    self._results[student_id] = (response, time.time())
            except Exception as e:
                logger.error(f"Synchronous API call failed for {student_id}: {str(e)}")
            finally:
                with self._lock:
                    self._pending.discard(student_id)
            return

        # Async background execution
        def target_call():
            try:
                response = api_service.send_verified_attendance(student_id, name, confidence)
                with self._lock:
                    self._results[student_id] = (response, time.time())
            except Exception as e:
                logger.error(f"Async API call failed for {student_id}: {str(e)}")
            finally:
                with self._lock:
                    self._pending.discard(student_id)

        thread = threading.Thread(target=target_call, name=f"APIDispatch-{student_id}")
        thread.daemon = True
        thread.start()

    def get_result(self, student_id):
        """
        Checks if a dispatched API call for the given student_id has completed.
        Returns a tuple of (completed: bool, response: AttendanceAPIResponse | None).
        """
        with self._lock:
            if student_id in self._results:
                response, _ = self._results[student_id]
                return True, response
            return False, None

    def is_pending(self, student_id):
        """
        Returns whether an API request is currently in-flight for the given student_id.
        """
        with self._lock:
            return student_id in self._pending

    def collect_expired(self, max_age_seconds=None):
        """
        Removes completed results that are older than the display window.
        Returns the number of removed entries.
        """
        if max_age_seconds is None:
            max_age_seconds = API_FEEDBACK_DISPLAY_SECONDS

        now = time.time()
        expired_keys = []

        with self._lock:
            for student_id, (_, timestamp) in list(self._results.items()):
                if now - timestamp > max_age_seconds:
                    expired_keys.append(student_id)

            for key in expired_keys:
                del self._results[key]

        return len(expired_keys)

    def cleanup(self, timeout=1.0):
        """
        Waits for all active threads to finish up to the timeout.
        """
        active_threads = [
            t for t in threading.enumerate() 
            if t.name.startswith("APIDispatch-")
        ]
        
        if not active_threads:
            return

        logger.info(f"Cleaning up {len(active_threads)} active API dispatcher threads...")
        start_time = time.time()
        
        for thread in active_threads:
            elapsed = time.time() - start_time
            rem = max(0.01, timeout - elapsed)
            if rem <= 0:
                break
            thread.join(timeout=rem)

        with self._lock:
            self._pending.clear()


class PerformanceBenchmark:
    """
    Measures and reports encoding load speed, per-frame processing time,
    recognition latency, and memory usage.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """
        Resets all collected benchmark statistics.
        """
        self._frame_times = []
        self._detection_times = []
        self._encoding_times = []
        self._comparison_times = []
        self._current_frame_start = None
        self._current_detection_start = None
        self._current_encoding_start = None
        self._current_comparison_start = None
        
        # System details
        self.sys_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cpu_count": multiprocessing.cpu_count(),
            "processor": platform.processor()
        }

    # --- Frame Timing Bracket API ---
    def start_frame(self):
        self._current_frame_start = time.perf_counter()

    def end_frame(self):
        if self._current_frame_start is not None:
            self._frame_times.append((time.perf_counter() - self._current_frame_start) * 1000.0)
            self._current_frame_start = None

    def start_detection(self):
        self._current_detection_start = time.perf_counter()

    def end_detection(self):
        if self._current_detection_start is not None:
            self._detection_times.append((time.perf_counter() - self._current_detection_start) * 1000.0)
            self._current_detection_start = None

    def start_encoding(self):
        self._current_encoding_start = time.perf_counter()

    def end_encoding(self):
        if self._current_encoding_start is not None:
            self._encoding_times.append((time.perf_counter() - self._current_encoding_start) * 1000.0)
            self._current_encoding_start = None

    def start_comparison(self):
        self._current_comparison_start = time.perf_counter()

    def end_comparison(self):
        if self._current_comparison_start is not None:
            self._comparison_times.append((time.perf_counter() - self._current_comparison_start) * 1000.0)
            self._current_comparison_start = None

    # --- Benchmark Execution API ---
    def benchmark_encoding_load(self, path, iterations=5):
        """
        Measures the time to load the encoding file N times and returns statistics.
        """
        path = Path(path)
        if not path.exists():
            return {"error": "File not found"}

        load_times = []
        cache = EncodingCache.get_instance()

        for _ in range(iterations):
            start = time.perf_counter()
            cache.load(path)
            load_times.append((time.perf_counter() - start) * 1000.0)

        # Get encoding stats
        stats = cache.get_stats()

        load_stats = {
            "avg_ms": sum(load_times) / len(load_times),
            "min_ms": min(load_times),
            "max_ms": max(load_times),
            "median_ms": sorted(load_times)[len(load_times) // 2],
            "iterations": iterations,
            "encoding_count": stats["encoding_count"],
            "file_size_bytes": stats["file_size_bytes"],
            "memory_estimate_bytes": stats["memory_estimate_bytes"]
        }
        return load_stats

    def benchmark_recognition(self, frame, face_locations, recognizer, iterations=10):
        """
        Measures identification latency for a set of face locations.
        """
        if frame is None or not face_locations or not recognizer:
            return {"error": "Invalid inputs"}

        latency_results = []
        
        for _ in range(iterations):
            for loc in face_locations:
                start = time.perf_counter()
                recognizer.identify(frame, loc)
                latency_results.append((time.perf_counter() - start) * 1000.0)

        if not latency_results:
            return {"error": "No recognition completed"}

        return {
            "avg_ms": sum(latency_results) / len(latency_results),
            "min_ms": min(latency_results),
            "max_ms": max(latency_results),
            "median_ms": sorted(latency_results)[len(latency_results) // 2],
            "iterations": iterations * len(face_locations)
        }

    def get_memory_info(self):
        """
        Returns memory footprint diagnostics.
        """
        cache = EncodingCache.get_instance()
        cache_stats = cache.get_stats()
        
        # Heap stats using tracemalloc
        current, peak = 0, 0
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()

        return {
            "encoding_matrix_bytes": cache_stats["memory_estimate_bytes"],
            "current_heap_bytes": current,
            "peak_heap_bytes": peak
        }

    def get_summary(self):
        """
        Returns a dictionary of all collected benchmark metrics.
        """
        summary = {
            "sys_info": self.sys_info,
            "frame_processing": {},
            "memory": self.get_memory_info()
        }

        # Calculate Frame stats
        if self._frame_times:
            summary["frame_processing"]["total_frames"] = len(self._frame_times)
            summary["frame_processing"]["avg_frame_time_ms"] = sum(self._frame_times) / len(self._frame_times)
            summary["frame_processing"]["min_frame_time_ms"] = min(self._frame_times)
            summary["frame_processing"]["max_frame_time_ms"] = max(self._frame_times)
        
        # Calculate Sub-phases
        if self._detection_times:
            summary["frame_processing"]["avg_detection_ms"] = sum(self._detection_times) / len(self._detection_times)
        if self._encoding_times:
            summary["frame_processing"]["avg_encoding_ms"] = sum(self._encoding_times) / len(self._encoding_times)
        if self._comparison_times:
            summary["frame_processing"]["avg_comparison_ms"] = sum(self._comparison_times) / len(self._comparison_times)

        return summary

    def print_summary(self):
        """
        Prints a formatted summary to console.
        """
        summary = self.get_summary()
        print("\n" + "=" * 50)
        print("AI Attendance System - Performance Summary")
        print("=" * 50)
        print(f"Platform: {summary['sys_info']['platform']}")
        print(f"Python:   {summary['sys_info']['python_version'].split()[0]}")
        print(f"CPUs:     {summary['sys_info']['cpu_count']}")
        print("-" * 50)
        
        fp = summary.get("frame_processing", {})
        if fp:
            print(f"Frames Processed: {fp.get('total_frames', 0)}")
            print(f"Avg Frame Time:   {fp.get('avg_frame_time_ms', 0.0):.2f} ms ({1000.0/fp.get('avg_frame_time_ms', 1.0) if fp.get('avg_frame_time_ms') else 0.0:.1f} FPS)")
            if "avg_detection_ms" in fp:
                print(f"  Detection Phase:  {fp['avg_detection_ms']:.2f} ms")
            if "avg_encoding_ms" in fp:
                print(f"  Encoding Phase:   {fp['avg_encoding_ms']:.2f} ms")
            if "avg_comparison_ms" in fp:
                print(f"  Comparison Phase: {fp['avg_comparison_ms']:.2f} ms")
        else:
            print("No frame processing data collected.")
            
        print("-" * 50)
        mem = summary.get("memory", {})
        print(f"Encoding Matrix Memory: {mem.get('encoding_matrix_bytes', 0) / 1024.0:.2f} KB")
        print(f"Peak Python Heap:       {mem.get('peak_heap_bytes', 0) / 1024.0 / 1024.0:.2f} MB")
        print("=" * 50)

    def generate_report(self, output_dir=None):
        """
        Writes a comprehensive timestamped report file to reports/.
        """
        if output_dir is None:
            output_dir = BENCHMARK_REPORT_DIR

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = self.get_summary()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"benchmark_report_{timestamp}.txt"

        fp = summary.get("frame_processing", {})
        mem = summary.get("memory", {})

        report_content = f"""=== AI Attendance System - Performance Benchmark Report ===
Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Python: {summary['sys_info']['python_version'].split()[0]} | Platform: {summary['sys_info']['platform']} | CPUs: {summary['sys_info']['cpu_count']}
Processor: {summary['sys_info']['processor']}

--- Frame Processing ---
Frames Processed: {fp.get('total_frames', 0)}
Avg Frame Time: {fp.get('avg_frame_time_ms', 0.0):.2f}ms ({1000.0/fp.get('avg_frame_time_ms', 1.0) if fp.get('avg_frame_time_ms') else 0.0:.1f} FPS)
Min Frame Time: {fp.get('min_frame_time_ms', 0.0):.2f}ms
Max Frame Time: {fp.get('max_frame_time_ms', 0.0):.2f}ms

--- Latency Breakdown ---
Detection: {fp.get('avg_detection_ms', 0.0):.2f}ms (Average)
Encoding: {fp.get('avg_encoding_ms', 0.0):.2f}ms (Average, Crop-then-Encode)
Comparison: {fp.get('avg_comparison_ms', 0.0):.2f}ms (Average)

--- Memory Footprint ---
Encoding Matrix: {mem.get('encoding_matrix_bytes', 0) / 1024.0:.2f} KB
Current Heap: {mem.get('current_heap_bytes', 0) / 1024.0 / 1024.0:.2f} MB
Peak Heap: {mem.get('peak_heap_bytes', 0) / 1024.0 / 1024.0:.2f} MB
"""

        with open(report_path, "w") as f:
            f.write(report_content)

        logger.info(f"Performance report generated successfully: {report_path.name}")
        return str(report_path)
