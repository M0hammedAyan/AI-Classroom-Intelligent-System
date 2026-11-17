Set-Location 'D:\CipherTECH\Projects\AI-Classroom-Intelligent-System'
$py='D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\.venv\Scripts\python.exe'
$d='D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\training_results\expanded_v3'
$env:PYTHONUNBUFFERED='1'
$pb=Start-Process $py -ArgumentList 'train_expanded_v3.py','--split','B' -NoNewWindow -PassThru -RedirectStandardOutput "$d\train_splitB.log" -RedirectStandardError "$d\train_splitB.err.log"
$null=$pb.Handle
$pb.Id | Out-File "$d\splitB.pid" -Encoding ascii
$pb.WaitForExit()
