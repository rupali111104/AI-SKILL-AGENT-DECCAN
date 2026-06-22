$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "Applying Kubernetes namespace and config..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

Write-Host "Creating local development secret..."
kubectl create secret generic recruitment-secrets `
  --namespace ai-recruitment `
  --from-literal=DATABASE_URL="postgresql://postgres:postgres@postgres:5432/recruitment" `
  --from-literal=POSTGRES_PASSWORD="postgres" `
  --from-literal=AWS_ACCESS_KEY_ID="local-dev" `
  --from-literal=AWS_SECRET_ACCESS_KEY="local-dev" `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "Deploying services..."
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/resume-service.yaml
kubectl apply -f k8s/skill-matching-service.yaml
kubectl apply -f k8s/question-generation-service.yaml
kubectl apply -f k8s/learning-plan-service.yaml
kubectl apply -f k8s/frontend.yaml

Write-Host "Deployment requested. Check rollout with:"
Write-Host "kubectl get pods -n ai-recruitment"
