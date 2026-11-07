# Backup VISTA development database
# Usage: .\scripts\backup_db.ps1

$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$backupDir = Join-Path -Path "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\..\db_backup" -ChildPath $timestamp
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item -Path "d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\backend\vista_dev.db" -Destination $backupDir -Force
Write-Host "Backup created at $backupDir\vista_dev.db"
