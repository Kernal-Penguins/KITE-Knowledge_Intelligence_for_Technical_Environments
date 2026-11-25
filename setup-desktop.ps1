# Put KITE on the Desktop and start it. Nothing is installed outside that folder
# except Docker images. Requires Docker Desktop and git.
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Kernal-Penguins/KITE-Knowledge_Intelligence_for_Technical_Environments.git"
$Branch = "cursor/desktop-setup-script-e6d7"
$Desktop = [Environment]::GetFolderPath("Desktop")
$Dest = Join-Path $Desktop "KITE"

Write-Host "KITE will live only in: $Dest"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is not installed. Install Git, then run this script again."
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw "Docker is not installed. Install Docker Desktop, start it, then run this script again. https://docs.docker.com/get-docker/"
}

if (Test-Path (Join-Path $Dest ".git")) {
  git -C $Dest fetch --depth 1 origin $Branch
  if ($LASTEXITCODE -ne 0) { throw "git fetch failed" }
  git -C $Dest checkout -B $Branch FETCH_HEAD
  if ($LASTEXITCODE -ne 0) { throw "git checkout failed" }
} elseif (-not (Test-Path (Join-Path $Dest "docker-compose.yml"))) {
  if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
  git clone --depth 1 --branch $Branch $RepoUrl $Dest
  if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
} else {
  throw "$Dest exists but is not a git checkout. Move that folder aside and run this script again."
}

Set-Location $Dest

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

$envText = Get-Content ".env" -Raw
if ($envText -notmatch "(?m)^GEMINI_API_KEY=\S+") {
  $key = $env:GEMINI_API_KEY
  if (-not $key) {
    Write-Host "The API will not start without a Gemini key."
    Write-Host "Create one at https://aistudio.google.com/apikey"
    $key = Read-Host "Paste GEMINI_API_KEY"
  }
  if (-not $key) {
    throw "No key entered. Edit $Dest\.env and run this script again."
  }
  if ($envText -match "(?m)^GEMINI_API_KEY=") {
    $envText = [regex]::Replace($envText, "(?m)^GEMINI_API_KEY=.*$", "GEMINI_API_KEY=$key")
  } else {
    $envText = $envText.TrimEnd() + "`r`nGEMINI_API_KEY=$key`r`n"
  }
  Set-Content -Path ".env" -Value $envText -NoNewline
}

$dockerUp = $false
try {
  docker info *> $null
  if ($LASTEXITCODE -eq 0) { $dockerUp = $true }
} catch {
  $dockerUp = $false
}
if (-not $dockerUp) {
  Write-Host "Waiting for Docker to start..."
  $ready = $false
  for ($i = 0; $i -lt 60; $i++) {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
  }
  if (-not $ready) {
    throw "Docker is not running. Start Docker Desktop, then run this script again."
  }
}

Write-Host "Building and starting KITE. The first run downloads images and can take several minutes."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "docker compose failed" }

$ok = $false
for ($i = 0; $i -lt 90; $i++) {
  try {
    $health = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/health" -TimeoutSec 3
    if ($health.StatusCode -eq 200) { $ok = $true; break }
  } catch {
    Start-Sleep -Seconds 2
  }
}

Write-Host ""
Write-Host "Project folder: $Dest"
Write-Host "App:            http://localhost:5173"
Write-Host "API docs:       http://localhost:8000/docs"
if (-not $ok) {
  throw "The API is not healthy yet. Check logs with: docker compose logs backend"
}
Start-Process "http://localhost:5173"
