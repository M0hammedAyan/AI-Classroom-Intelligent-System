Set-Location 'D:\CipherTECH\Projects\AI-Classroom-Intelligent-System'
$py='D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\.venv\Scripts\python.exe'
$d='D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\training_results\expanded_v3'
$env:PYTHONUNBUFFERED='1'
function Test-SplitOk($s){
 (Test-Path "$d\best_model_expanded_v3_split$s.pth") -and ((Select-String -Path "$d\train_split$s.log","$d\train_split$s.err.log" -Pattern 'saved checkpoint' -Quiet -ErrorAction SilentlyContinue) -eq $true)
}
$pa=Start-Process $py -ArgumentList 'train_expanded_v3.py','--split','A' -NoNewWindow -PassThru -RedirectStandardOutput "$d\train_splitA.log" -RedirectStandardError "$d\train_splitA.err.log"
$null=$pa.Handle  # cache handle so ExitCode is available (not used for the decision)
$pa.WaitForExit()
if(Test-SplitOk 'A'){
 $pb=Start-Process $py -ArgumentList 'train_expanded_v3.py','--split','B' -NoNewWindow -PassThru -RedirectStandardOutput "$d\train_splitB.log" -RedirectStandardError "$d\train_splitB.err.log"
 $null=$pb.Handle
 $pb.WaitForExit()
}
