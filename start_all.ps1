param(
    [string]$ProjectRoot = "D:\final_project",
    [string]$BackendHost = "0.0.0.0",
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Stop"

$backendDir = Join-Path $ProjectRoot "backend_django"
$frontendDir = Join-Path $ProjectRoot "frontend_vue"

if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found: $backendDir"
}
if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

# 先释放 8000/5173，避免重复 start 导致多实例、端口冲突（表现为“有时能用有时不能”）
$stopScript = Join-Path $ProjectRoot "stop_all.ps1"
if (Test-Path $stopScript) {
    Write-Host "Stopping existing backend/frontend processes..." -ForegroundColor Yellow
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $stopScript | Out-Host
    } finally {
        $ErrorActionPreference = $prevEap
    }
    Start-Sleep -Seconds 1
}

${backendAddr} = "${BackendHost}:${BackendPort}"
$backendCommand = @"
`$env:DB_HOST='127.0.0.1'
`$env:DB_PORT='3306'
`$env:DB_NAME='pose_system'
`$env:DB_USER='pose_app'
`$env:DB_PASSWORD='pose_app_123'
# 推理使用 COCO-WholeBody 微调权重（epoch1 最优），不是 MMPose 官方预训练别名
`$env:MODEL_NAME='model_artifacts/rtmw_m_wholebody_256x192_a10_finetune.py'
`$env:MODEL_CHECKPOINT='model_artifacts/best_coco-wholebody_AP_epoch_1.pth'
`$env:MODEL_DISPLAY_NAME='RTMW-M-WholeBody-Finetune'
`$env:MODEL_DEVICE='cpu'
`$env:VIDEO_INFER_FRAME_STRIDE='2'
`$env:DOUBAO_MODEL='doubao-seed-2-0-mini-260215'
`$env:DOUBAO_API_KEY='faadeb5b-1b22-4be3-a955-c653b3a872c0'
`$env:DOUBAO_BASE_URL='https://ark.cn-beijing.volces.com/api/v3'
`$env:DOUBAO_TIMEOUT='40'
`$env:INIT_ADMIN_USERNAME='admin'
`$env:INIT_ADMIN_EMAIL='admin@example.com'
`$env:INIT_ADMIN_PASSWORD='Admin@123456'
python manage.py migrate --noinput
python manage.py init_pose_system
python manage.py runserver $backendAddr
"@

$frontendCommand = "npm run dev"

Start-Process powershell -WorkingDirectory $backendDir -ArgumentList "-NoExit", "-Command", $backendCommand | Out-Null
Start-Sleep -Milliseconds 500
Start-Process powershell -WorkingDirectory $frontendDir -ArgumentList "-NoExit", "-Command", $frontendCommand | Out-Null

# migrate + init + runserver 通常需 5–15 秒；原 2 秒检测几乎总会误报“未就绪”
$backendListening = $null
$maxWaitSec = 20
for ($i = 0; $i -lt $maxWaitSec; $i++) {
    Start-Sleep -Seconds 1
    $backendListening = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    if ($backendListening) { break }
}

Write-Host "Backend and frontend windows started." -ForegroundColor Green
Write-Host "Backend: http://$BackendHost`:$BackendPort" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "LAN access: use your local IP on port 5173 (e.g. http://192.168.3.10:5173)" -ForegroundColor Yellow
if ($backendListening) {
    Write-Host "Backend port $BackendPort is listening (waited about $($i + 1)s)." -ForegroundColor Green
} else {
    Write-Host "Warning: backend port $BackendPort still not listening after ${maxWaitSec}s. Check the backend PowerShell window for errors (DB / port in use / missing deps)." -ForegroundColor Yellow
}
