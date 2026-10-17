"""
VISTA — Split A Training Launcher  (80 % train / 10 % val / 10 % test)
=======================================================================
Thin wrapper around train.py that runs only Split A.

Usage:
    python train_splitA.py

Outputs (written to this directory):
    best_model_splitA.pth
    results_splitA.txt
    confusion_matrix_splitA.png
    training_curve_splitA.png
    data_split_log.txt  (Split A section appended)
"""

import sys
from pathlib import Path

# Ensure train.py (in the same directory) is importable regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

from train import main  # noqa: E402

if __name__ == "__main__":
    main(splits=["A"])
