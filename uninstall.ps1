#!/usr/bin/env pwsh
# claude-shorts uninstaller for Windows

$ErrorActionPreference = "Stop"

Write-Host "=== Uninstalling claude-shorts ===" -ForegroundColor Cyan
Write-Host ""

$SkillDir = Join-Path $env:USERPROFILE ".claude" "skills" "shorts"
if (Test-Path $SkillDir) {
    Remove-Item -Recurse -Force $SkillDir
    Write-Host "  Removed: $SkillDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== claude-shorts uninstalled ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart Claude Code to complete removal." -ForegroundColor Yellow
