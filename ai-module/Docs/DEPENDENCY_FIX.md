# 🛠️ Dependency Fix: Installing dlib and face_recognition on Windows

Installing `face_recognition` often fails because `dlib` cannot be compiled without C++ Build Tools. Follow these verified steps to install a pre-compiled version.

## Step 1: Install CMake
Run this command in your terminal first (if not already installed):
```powershell
pip install cmake
```

## Step 2: Install Pre-compiled dlib
Since you are using **Python 3.10**, the most reliable way to install `dlib` without build tools is using the `dlib-bin` package:
```powershell
pip install dlib-bin
```
*Note: This package provides the `dlib` library directly.*

## Step 3: Install face_recognition and dependencies
To prevent `pip` from trying to build `dlib` from source, install the other dependencies manually first, then install `face_recognition` without checking dependencies:
```powershell
pip install face-recognition-models numpy Pillow Click
pip install face_recognition --no-deps
```

## Step 4: Verify
Run the detection test to confirm the installation is working and the red squiggly lines in the IDE are gone:
```powershell
python -m ai_module.tests.test_detection
```

