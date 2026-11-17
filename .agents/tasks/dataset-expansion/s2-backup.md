# S2 Backup baseline

Status: OK, all sizes match. Destination: training_results/baseline_before_expansion/ (evaluation json in evaluation_results/).

'Delete and compare' is implemented as: new graphs replace the old ones in the main training_results view, old ones live in baseline_before_expansion, and a comparison report is produced.

.pth files are >50MB; 'training_results/baseline_before_expansion/*.pth' appended to .gitignore.

| File | Source bytes | Backup bytes |
|---|---|---|
| training_results/best_model_npz_splitA.pth | 98634915 | 98634915 |
| training_results/best_model_npz_splitB.pth | 98634915 | 98634915 |
| training_results/confusion_matrix_npz_splitA.png | 172700 | 172700 |
| training_results/confusion_matrix_npz_splitB.png | 168250 | 168250 |
| training_results/confusion_matrix_splitA.png | 180338 | 180338 |
| training_results/confusion_matrix_splitB.png | 182711 | 182711 |
| training_results/data_split_npz_log.txt | 4354416 | 4354416 |
| training_results/results_npz_splitA.txt | 3932 | 3932 |
| training_results/results_npz_splitB.txt | 3934 | 3934 |
| training_results/training_curve_npz_splitA.png | 78000 | 78000 |
| training_results/training_curve_npz_splitB.png | 84752 | 84752 |
| training_results/training_curve_splitA.png | 105597 | 105597 |
| training_results/training_curve_splitB.png | 107579 | 107579 |
| evaluation/results/cascade_ablation.json | 1100 | 1100 |
| evaluation/results/coach_groundedness.json | 5132 | 5132 |
| evaluation/results/latency_benchmark.json | 1963 | 1963 |
| evaluation/results/recognition_threshold_sweep.json | 3362 | 3362 |
| evaluation/results/risk_model_evaluation.json | 2497 | 2497 |

