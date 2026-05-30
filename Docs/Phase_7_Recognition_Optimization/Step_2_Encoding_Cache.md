# Step 2: Encoding Cache (Singleton Manager)

## Objective
Create a thread-safe singleton `EncodingCache` class in `ai_module/optimization.py` that loads face encodings once into memory and serves them to all components without repeated disk I/O.

## Why This Step
The current `EncodingManager` in `utils.py` reads the pickle file on every instantiation. If multiple components create their own `EncodingManager`, the file is read multiple times. The singleton cache eliminates this overhead and stores encodings in an optimized NumPy matrix format.

## Tasks

1. Create `ai_module/optimization.py` with the `EncodingCache` class.

2. Implement thread-safe singleton pattern:
   - Use `threading.Lock()` to ensure only one instance is created, even under concurrent access.
   - `EncodingCache.get_instance()` returns the single shared instance.

3. Implement encoding loading:
   - Read `encodings.pickle` using `pickle.load()`.
   - Convert the list of encoding arrays into a single `np.ndarray` of shape `(N, 128)` for vectorized distance computation.
   - Store the corresponding names list.
   - Record load time for performance statistics.

4. Implement file-change detection:
   - Store the file's `os.path.getmtime()` timestamp on load.
   - `reload_if_changed()` compares stored timestamp with current timestamp.
   - If file has changed (e.g., new student registered), reload encodings transparently.
   - Check interval controlled by `ENCODING_RELOAD_CHECK_SECONDS` config.

5. Implement cache validation:
   - On load, verify that `data["encodings"]` and `data["names"]` exist and have matching lengths.
   - Handle corrupted pickle files gracefully (log error, continue with empty cache).
   - Handle missing encoding file (log warning, empty cache).

6. Implement statistics API:
   - `get_stats()` returns dict with: encoding count, file size, load time (ms), memory estimate, last reload timestamp.
   - `is_loaded()` returns boolean.

7. Implement cache accessors:
   - `get_encodings()` returns `(np.ndarray, list[str])` tuple of (encoding matrix, names).
   - Returns `(np.empty((0, 128)), [])` if cache is empty.

## Design Details

```
EncodingCache (Singleton)
├── _instance: EncodingCache (class-level)
├── _lock: threading.Lock (class-level)
├── _encodings: np.ndarray (N×128)
├── _names: list[str]
├── _file_mtime: float
├── _last_check_time: float
├── _load_time_ms: float
├── get_instance() → EncodingCache
├── load(path) → None
├── reload_if_changed() → bool
├── get_encodings() → tuple[np.ndarray, list[str]]
├── get_stats() → dict
└── is_loaded() → bool
```

## Dependencies
- Step 1 (config values: `ENCODING_FILE`, `ENCODING_RELOAD_CHECK_SECONDS`)

## Files Created
- `ai_module/optimization.py` (initial creation with `EncodingCache`)

## Expected Outcome
A single `EncodingCache` instance loads encodings once, serves them efficiently as a NumPy matrix, and automatically detects when the encoding file changes to reload transparently.
