# Local Run Scripts

Use these scripts from PowerShell after Docker Desktop is running.

Check installed tools:

```powershell
.\scripts\check_environment.ps1
```

Run the full Docker Compose stack:

```powershell
.\scripts\run_docker_stack.ps1
```

Deploy the Kubernetes manifests to the current Kubernetes context:

```powershell
.\scripts\deploy_kubernetes_local.ps1
```

Docker Desktop must be open and running before the Docker or Kubernetes scripts can work.
