$R = "D:\CipherTECH\Projects\AI-Classroom-Intelligent-System"
$env:VISTA_DB_URL = "sqlite:///D:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/backend/vista_dev.db"
$env:VISTA_FACE_MODEL = "$R\training_results\expanded_v3\best_model_expanded_v3_splitB.pth"
$env:VISTA_FACE_MODEL_THRESHOLD = "0.60"
$env:PYTHONPATH = $R
$p = Start-Process -FilePath "$R\.venv\Scripts\python.exe" -ArgumentList "-m","uvicorn","backend.app.main:app","--host","127.0.0.1","--port","8002" -WorkingDirectory "$R\vista" -RedirectStandardOutput "$R\training_results\expanded_v3\e2e_backend.log" -RedirectStandardError "$R\training_results\expanded_v3\e2e_backend.err.log" -WindowStyle Hidden -PassThru
$p.Id | Out-File "$R\training_results\expanded_v3\e2e_backend.pid"
