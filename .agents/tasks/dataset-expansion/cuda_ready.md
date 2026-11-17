# CUDA ready

- NVIDIA driver: 596.08 (max CUDA 13.2)
- PyTorch index: cu132 (https://download.pytorch.org/whl/cu132)
- Installed: torch 2.15.0+cu132, torchvision 0.29.2+cu132 (torch.version.cuda = 13.2)
- torch.cuda.is_available(): True
- GPU: NVIDIA GeForce RTX 3050 6GB Laptop GPU
- ResNet-50, batch 32 x 3x160x160, AMP fp16, forward+backward+SGD step:
  - GPU: 0.089 s/step, peak allocated memory 939 MB (batch 32 fits in 6 GB easily)
  - CPU: 1.67 s/step (1 step), rough speedup ~19x
- Tests: 143 passed, 5 errors (pre-existing, tests/test_timetable.py), same as before
- The app still defaults to CPU. VISTA_FACE_MODEL_DEVICE is not set.
- Pre-change pip freeze: .agents/tasks/dataset-expansion/pip_freeze_before_cuda.txt

Revert:

    .\.venv\Scripts\python.exe -m pip install torch==2.15.0 torchvision==0.29.2 --index-url https://download.pytorch.org/whl/cpu
