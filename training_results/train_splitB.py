"""
VISTA — Split B Training Launcher  (70 % train / 15 % val / 15 % test)
=======================================================================
Thin wrapper around train.py that runs only Split B.

Usage:
    python train_splitB.py

Outputs (written to this directory):
    best_model_splitB.pth
    results_splitB.txt
    confusion_matrix_splitB.png
    training_curve_splitB.png
    data_split_log.txt  (Split B section appended)
"""

import sys
from pathlib import Path

# Ensure train.py (in the same directory) is importable regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

from train import main  # noqa: E402

if __name__ == "__main__":
    main(splits=["B"])
