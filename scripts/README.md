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

The default stack uses a lightweight local embedding fallback so Docker can build quickly. To test the heavier Sentence Transformers image later, run:

```powershell
docker compose -f docker-compose.yml -f docker-compose.ml.yml up --build skill-matching-service
```

Deploy the Kubernetes manifests to the current Kubernetes context:

```powershell
.\scripts\deploy_kubernetes_local.ps1
```

Docker Desktop must be open and running before the Docker or Kubernetes scripts can work.
