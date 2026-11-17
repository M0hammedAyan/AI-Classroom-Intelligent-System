# Baseline hyperparameters (results_npz_splitA/B.txt)

Common: ResNet-50 (ImageNet pretrained, ArcFace preprocessing), Adam, lr 1e-4, CrossEntropyLoss, batch 32, max 30 epochs, early-stop patience 7, input 112x112 mean=0.5 std=0.5, seed 42 (train.py). Data: data/processed/facial_pipeline_results.npz; train uses all 30 aug variants, val/test use aug_idx==0 only.

| | Split A (80/10/10) | Split B (70/15/15) |
|---|---|---|
| Train / Val / Test samples | 16,080 / 67 / 68 | 14,070 / 101 / 101 |
| Epochs run (early stop) | 8 | 8 |
| Best epoch | 1 | 1 |
| Best val acc | 88.06% | 93.07% |
| Final train acc | 96.55% | 96.50% |
| Test acc | 86.76% | 90.10% |
| Train/Test gap | 9.78% | 6.40% |
