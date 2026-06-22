$ErrorActionPreference = "Continue"

Write-Host "Checking Docker..."
docker --version
docker compose version
docker info --format "Docker engine: {{.ServerVersion}}"

Write-Host ""
Write-Host "Checking Kubernetes..."
kubectl version --client
kubectl config current-context

Write-Host ""
Write-Host "If Docker engine is unavailable, open Docker Desktop and wait until it says Docker is running."
