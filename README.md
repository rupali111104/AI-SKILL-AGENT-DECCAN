# TalentFit AI - Cloud-Native AI Recruitment Platform

TalentFit AI is an upgraded AI recruitment platform that analyzes a candidate resume against a target job description, identifies skill gaps, generates technical assessment questions, and creates a personalized learning roadmap.

The project started as a college-style AI skill assessment agent. It is now structured like a production software engineering system: React frontend, independent FastAPI microservices, Docker containers, Kubernetes manifests, PostgreSQL persistence, S3-compatible resume storage, and GitHub Actions CI/CD.

## Platform Story

Instead of building one monolithic AI application, TalentFit AI separates each responsibility into its own service:

```text
React Frontend
    |
Resume Service API
    |
    |-- stores resume object in S3 or local object storage
    |-- extracts PDF/DOCX text
    |-- forwards skills to Skill Matching Service
    |-- asks Question Generation Service for interview questions
    |-- asks Learning Plan Service for a roadmap
    |-- stores analysis result in PostgreSQL
    |
Recruiter/Candidate Result Dashboard
```

This design demonstrates the kind of architecture used in larger engineering teams: each service has a clear contract, can be deployed independently, can scale independently, and can be tested without changing the whole platform.

## Main Features

1. Upload a candidate resume from the React frontend.
2. Extract text from PDF and DOCX resumes.
3. Store uploaded resumes in AWS S3 in production or local object storage during development.
4. Extract candidate skills and required job skills.
5. Match candidate skills against a job description.
6. Compute semantic similarity with Sentence Transformers in the matching service.
7. Store analysis results in PostgreSQL.
8. Generate technical interview questions from missing and matched skills.
9. Generate a personalized learning roadmap.
10. Run each service in its own Docker container.
11. Deploy services to Kubernetes with Deployments and Services.
12. Use GitHub Actions to validate, build Docker images, push to GHCR, and deploy.

## Tech Stack

Frontend:
- React
- Vite
- Axios

Backend and services:
- FastAPI
- Python
- pypdf
- python-docx
- httpx
- Sentence Transformers
- PostgreSQL
- AWS S3 or local object storage fallback

Cloud-native:
- Docker
- Docker Compose
- Kubernetes Deployments and Services
- GitHub Actions
- GitHub Container Registry

## Project Structure

```text
AI-SKILL-AGENT-DECCAN/
  FRONTEND/
    src/
    Dockerfile

  BACKEND/
    app/
    requirements.txt

  SERVICES/
    common/
      skills.py
      vectors.py
      storage.py
      database.py
    resume-service/
      app.py
      Dockerfile
      requirements.txt
    skill-matching-service/
      app.py
      Dockerfile
      requirements.txt
    question-generation-service/
      app.py
      Dockerfile
      requirements.txt
    learning-plan-service/
      app.py
      Dockerfile
      requirements.txt

  k8s/
    namespace.yaml
    configmap.yaml
    secret.example.yaml
    frontend.yaml
    resume-service.yaml
    skill-matching-service.yaml
    question-generation-service.yaml
    learning-plan-service.yaml
    postgres.yaml

  .github/workflows/
    cloud-native-ci.yml

  docker-compose.yml
  start_phase1.ps1
```

## Service Responsibilities

Resume Service:
- Receives resume and job description uploads.
- Stores resume objects in S3 or local object storage.
- Extracts text from PDF/DOCX.
- Calls downstream services.
- Persists final analysis results in PostgreSQL when `DATABASE_URL` is configured.

Skill Matching Service:
- Receives resume text, job description text, and extracted skills.
- Compares required skills with candidate skills.
- Uses Sentence Transformers when available.
- Falls back to deterministic local vectors for lightweight local demos.
- Returns matched skills, missing skills, extra skills, match score, and semantic similarity.

Question Generation Service:
- Generates practical and conceptual technical questions.
- Prioritizes missing skills first, then matched skills.

Learning Plan Service:
- Builds a prioritized roadmap for missing or weak skills.
- Includes learning goals, resources, mini projects, and time estimates.

## Run The Original Local Demo

The original local demo is still available and useful for quick presentations:

```powershell
.\start_phase1.ps1
```

Frontend:

```text
http://127.0.0.1:5173
```

Backend:

```text
http://127.0.0.1:8000
```

## Run The Cloud-Native Stack Locally

Use Docker Compose from the project root. The default stack uses the lightweight local vector fallback so the full platform can build reliably on normal laptops:

```powershell
docker compose up --build
```

Services:

```text
Frontend:                    http://localhost:5173
Resume Service:              http://localhost:8000
Skill Matching Service:      http://localhost:8001
Question Generation Service: http://localhost:8002
Learning Plan Service:       http://localhost:8003
PostgreSQL:                  localhost:5432
```

To build the heavier Sentence Transformers version of the Skill Matching Service, use the optional ML compose override:

```powershell
docker compose -f docker-compose.yml -f docker-compose.ml.yml up --build skill-matching-service
```

That ML build downloads large packages such as Torch, so the first build can take a long time and needs a stable Docker Desktop session.

## Kubernetes Deployment

The Kubernetes manifests are in `k8s/`.

Before deploying, create a real secret from `k8s/secret.example.yaml` and replace:

- `DATABASE_URL`
- `POSTGRES_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Also replace the placeholder `OWNER` in image names with your GitHub Container Registry owner or organization.

Example deploy:

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/resume-service.yaml
kubectl apply -f k8s/skill-matching-service.yaml
kubectl apply -f k8s/question-generation-service.yaml
kubectl apply -f k8s/learning-plan-service.yaml
kubectl apply -f k8s/frontend.yaml
```

## CI/CD

The GitHub Actions workflow in `.github/workflows/cloud-native-ci.yml` does three things:

1. Validates frontend lint/build and Python compilation.
2. Builds Docker images for the frontend and each service.
3. Pushes images to GitHub Container Registry and deploys Kubernetes manifests on pushes to `main`.

Required GitHub secret:

```text
KUBE_CONFIG
```

The workflow uses GitHub's built-in `GITHUB_TOKEN` to publish images to GHCR.

## Interview Explanation

You can explain the project like this:

```text
I upgraded a simple AI resume analyzer into a cloud-native recruitment platform.
The React frontend uploads resumes to a Resume Service. That service stores files in S3,
extracts resume text, and coordinates separate microservices for skill matching,
question generation, and learning-plan generation. The matching service uses Sentence
Transformers for semantic similarity, and final results are stored in PostgreSQL.
Each service runs in its own Docker container and is deployed to Kubernetes using
Deployments and Services, so the system can scale each workload independently.
GitHub Actions validates the app, builds images, pushes them to GHCR, and deploys
updates automatically.
```

This shows React, APIs, microservices, Docker, Kubernetes, databases, cloud storage, CI/CD, and AI/ML in one coherent software engineering project.
