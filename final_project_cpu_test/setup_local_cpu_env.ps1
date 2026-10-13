param(
    [string]$ProjectRoot = "",
    [string]$PythonExe = "python",
    [int]$Samples = 3,
    [string]$Split = "val2017",
    [ValidateSet("lite", "full")]
    [string]$InstallProfile = "lite",
    [ValidateSet("auto", "full", "lite")]
    [string]$TestMode = "auto",
    [switch]$SkipInstall,
    [switch]$RunTest = $true
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$VenvPath = Join-Path $ProjectRoot "final_project_cpu_test\.venv_cpu_test"
$ReqPathLite = Join-Path $ProjectRoot "final_project_cpu_test\requirements_cpu_smoke.txt"
$ReqPathFull = Join-Path $ProjectRoot "backend_django\requirements.txt"
$ReqPath = if ($InstallProfile -eq "full") { $ReqPathFull } else { $ReqPathLite }
$TestScript = Join-Path $ProjectRoot "final_project_cpu_test\run_cpu_smoke_test.py"
$DataRoot = Join-Path $ProjectRoot "coco-wholebody"
$OutputDir = Join-Path $ProjectRoot "final_project_cpu_test\outputs"

Write-Host "[INFO] ProjectRoot: $ProjectRoot"
Write-Host "[INFO] VenvPath   : $VenvPath"
Write-Host "[INFO] Profile    : $InstallProfile"
Write-Host "[INFO] TestMode   : $TestMode"

function Invoke-Checked {
    param([string]$StepName, [scriptblock]$Command)
    Write-Host "[STEP] $StepName"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "[ERROR] Step failed: $StepName (exit=$LASTEXITCODE)"
    }
}

if (!(Test-Path $ReqPath)) {
    throw "[ERROR] requirements not found: $ReqPath"
}

if (!(Test-Path $TestScript)) {
    throw "[ERROR] smoke test script not found: $TestScript"
}

if (!(Test-Path $VenvPath)) {
    Invoke-Checked "Creating virtual environment..." { & $PythonExe -m venv $VenvPath }
}

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
if (!(Test-Path $VenvPython)) {
    throw "[ERROR] venv python not found: $VenvPython"
}

if (-not $SkipInstall) {
    Invoke-Checked "Installing bootstrap tools..." { & $VenvPython -m pip install --upgrade pip setuptools wheel }
    Invoke-Checked "Installing dependencies from $ReqPath ..." { & $VenvPython -m pip install -r $ReqPath }
}

if ($RunTest) {
    Invoke-Checked "Running CPU smoke test..." {
        & $VenvPython $TestScript `
            --project-root $ProjectRoot `
            --data-root $DataRoot `
            --split $Split `
            --samples $Samples `
            --mode $TestMode `
            --output-dir $OutputDir
    }
}

Write-Host "[DONE] Setup finished."
