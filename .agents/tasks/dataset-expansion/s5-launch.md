# S5a Launch retrain

Start: 2026-11-16 20:46:28 +05:30. Both splits run in parallel on CPU (no CUDA), detached hidden processes.

| Split | PID | Log (stdout) | stderr |
|---|---|---|---|
| A (80/10/10) | 11148 | training_results/expanded/train_splitA.log | train_splitA.err.log |
| B (70/15/15) | 8628 | training_results/expanded/train_splitB.log | train_splitB.err.log |

Command (cwd R, env PYTHONUNBUFFERED=1, PYTHONIOENCODING=utf-8):
`.venv\Scripts\python.exe train_expanded.py --split A --epochs 30` (and `--split B`)

Epochs: 30 max (baseline value), early-stop patience 7, other hyperparameters as in s2-baseline-hparams.md. Not reduced.
First epoch (split A, both running): 186 s. Worst case 30 epochs ~93 min; early stop likely shorter.

Gate file: `.agents/tasks/dataset-expansion/train_status.json` = {"done":"no"} (not changed by the training; a later step sets it to yes).

Check: `Get-Content -Tail 20 D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\training_results\expanded\train_splitA.log` (same for B). Alive: `Get-Process -Id 11148,8628`. Final outputs: results_expanded_splitA/B.txt, history_expanded_splitA/B.json in training_results/expanded/.
