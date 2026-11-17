$in = "D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1)_updated.docx"
$out = "D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\1report\3Report (1)_updated.pdf"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$d = $w.Documents.Open($in, $false, $true)
$d.SaveAs2($out, 17)
"pages: " + $d.ComputeStatistics(2)
$d.Close($false)
$w.Quit()
