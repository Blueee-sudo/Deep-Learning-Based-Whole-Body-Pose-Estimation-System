param(
    [int[]]$Ports = @(8000, 5173)
)

$ErrorActionPreference = "SilentlyContinue"

$stoppedPids = New-Object System.Collections.Generic.HashSet[int]

function Stop-ByPid {
    param([int]$PidToStop)
    if ($PidToStop -le 0) { return }
    if ($stoppedPids.Contains($PidToStop)) { return }
    try {
        Stop-Process -Id $PidToStop -Force -ErrorAction SilentlyContinue
        $stoppedPids.Add($PidToStop) | Out-Null
        Write-Host "已停止进程 PID=$PidToStop" -ForegroundColor Yellow
    } catch {
        # ignore
    }
}

# 1) 按端口停止（最准确）；端口空闲时 Get-NetTCPConnection 无结果，不能当错误
foreach ($port in $Ports) {
    $listeners = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
    foreach ($conn in $listeners) {
        if ($conn.OwningProcess -gt 0) {
            Stop-ByPid -PidToStop $conn.OwningProcess
        }
    }
}

# 2) 按命令行特征兜底停止（防止尚未监听端口）
$targets = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    ($_.Name -match "python|node|npm") -and (
        $_.CommandLine -match "manage\.py\s+runserver" -or
        $_.CommandLine -match "\bvite\b" -or
        $_.CommandLine -match "npm\s+run\s+dev"
    )
}

foreach ($p in $targets) {
    Stop-ByPid -PidToStop $p.ProcessId
}

if ($stoppedPids.Count -eq 0) {
    Write-Host "未找到需要停止的前后端进程（8000/5173）" -ForegroundColor Cyan
} else {
    Write-Host "已停止 $($stoppedPids.Count) 个相关进程。" -ForegroundColor Green
}
