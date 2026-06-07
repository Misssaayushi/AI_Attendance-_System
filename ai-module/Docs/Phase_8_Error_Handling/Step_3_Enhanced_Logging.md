# Step 3: Enhanced Logging

## Objective
Upgrade the logging system in `utils.py` to support log file rotation and structured log formatting — preventing unbounded log file growth and making logs easier to search and filter.

## Why This Step
The current `ai_system.log` file is already 443 KB and grows without bound. In a long demo session, this could consume significant disk space. Additionally, the current log format (`timestamp - name - level - message`) doesn't include event type categorization, making it hard to grep for specific events like recognition results vs. errors vs. API calls.

## Tasks

1. Update `get_logger()` function in `utils.py`:
   - Replace `logging.FileHandler` with `logging.handlers.RotatingFileHandler`
   - Configure max file size from `LOG_ROTATION_MAX_BYTES` (default 5 MB)
   - Configure backup count from `LOG_ROTATION_BACKUP_COUNT` (default 3)
   - This means: `ai_system.log` (current) + `ai_system.log.1`, `.2`, `.3` (backups)
   - When the current file reaches 5 MB, it rotates automatically

2. Update log formatter to include structured prefixes:
   - Format: `%(asctime)s | %(name)s | %(levelname)s | %(message)s`
   - The pipe separator (`|`) makes it easier to parse with command-line tools
   - Example output:
     ```
     2026-05-30 10:15:30 | FaceRecognizer | INFO | Identified: 1_Aayushi (confidence: 92.5%)
     2026-05-30 10:15:31 | CameraHandler | WARNING | Failed to read frame from webcam
     2026-05-30 10:15:32 | ErrorTracker | ERROR | [RECOVERABLE] Webcam disconnected
     ```

3. Preserve backward compatibility:
   - `get_logger("name")` still returns a standard `logging.Logger`
   - Existing code calling `logger.info()`, `logger.error()`, etc. works unchanged
   - The only visible change is the log format and automatic rotation

4. Import `RotatingFileHandler` from `logging.handlers` (part of Python stdlib, no new dependency).

5. Add new config imports to `utils.py`:
   - `LOG_ROTATION_MAX_BYTES`
   - `LOG_ROTATION_BACKUP_COUNT`

## Design Details

### Before (Current)
```python
file_handler = logging.FileHandler(LOG_FILE)
```

### After (Enhanced)
```python
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_ROTATION_MAX_BYTES,
    backupCount=LOG_ROTATION_BACKUP_COUNT
)
```

### Log Rotation Behavior
```
ai_system.log       ← current, actively written to
ai_system.log.1     ← previous rotation
ai_system.log.2     ← older rotation
ai_system.log.3     ← oldest rotation (deleted when .2 rotates)
```

## Dependencies
- Step 1 (config values: `LOG_ROTATION_MAX_BYTES`, `LOG_ROTATION_BACKUP_COUNT`)

## Files Modified
- `ai_module/utils.py` (update `get_logger()` function only)

## Expected Outcome
Log files are automatically rotated at 5 MB, keeping a maximum of 20 MB total (4 files). Log format includes pipe-separated fields for easier filtering. All existing logging calls work unchanged.
