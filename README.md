# AI-Powered CI/CD & DevOps Automation Platform

A practical CI/CD and DevOps project built around a FastAPI application. The main goal is to automate the software delivery process from code changes to deployment, while adding security checks, AI-assisted analysis, and automatic failure recovery.

## Overview

The project uses **GitHub Actions** as the main CI/CD engine and **Docker** to build and deploy the application. **n8n** is used as an automation layer for deployment notifications and failure handling, while **Ollama with Qwen2.5-Coder** provides AI-assisted code review and deployment failure analysis.

The pipeline follows this flow:

```text
Code Push
   ↓
Tests & Code Quality
   ↓
Security Checks
   ↓
AI Code Review
   ↓
Docker Build
   ↓
Deployment
   ↓
Health Check
   ↓
Success / Rollback
```

The application is a small FastAPI e-commerce API used as the workload for the CI/CD system. The focus of the project is not the application itself, but the infrastructure and automation around building, testing, securing, and deploying it.

The pipeline runs automated tests with **Pytest**, code-quality checks with **Ruff**, dependency scanning with **pip-audit**, and secret scanning with **Gitleaks**.

An AI review stage uses **Ollama and Qwen2.5-Coder** to analyze changed Python code. The AI provides additional feedback, while deployment decisions remain based on predefined CI/CD rules.

Docker images are built and stored in **GitHub Container Registry**, with each image tagged using its Git commit SHA. This makes it possible to identify exactly which version is deployed.

After deployment, the application is checked through its `/health` endpoint. If the new version fails the health check, the pipeline automatically restores the previous Docker image and verifies that the rollback was successful.

**n8n** receives deployment events through a webhook. Successful deployments trigger an email notification, while failed deployments are analyzed by Ollama and reported through an automatically created GitHub Issue.

## CI/CD Pipeline

* **Testing:** Pytest
* **Code Quality:** Ruff
* **Security:** pip-audit and Gitleaks
* **AI Review:** Ollama + Qwen2.5-Coder
* **Build:** Docker
* **Registry:** GitHub Container Registry
* **Deployment:** Docker Compose
* **Health Checks:** `/health`
* **Rollback:** Previous Docker image
* **Automation:** n8n

## Technology Stack

| Area       | Technologies                |
| ---------- | --------------------------- |
| Backend    | Python, FastAPI, SQLAlchemy |
| Database   | PostgreSQL                  |
| CI/CD      | GitHub Actions              |
| Containers | Docker, Docker Compose      |
| Security   | pip-audit, Gitleaks         |
| AI         | Ollama, Qwen2.5-Coder       |
| Automation | n8n                         |
| Registry   | GitHub Container Registry   |

## Project Structure

```text
ai-devops-platform/
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
├── tests/
│   ├── conftest.py
│   └── test_products.py
├── ai_reviewer/
│   └── reviewer.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── ruff.toml
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/FirasObieda/ai-devops-platform.git
cd ai-devops-platform
```

### 2. Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the environment

Create a `.env` file:

```env
DATABASE_URL=<your-database-url>
```

Do not commit `.env` to the repository.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 6. Run validation

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest
ruff check .
pip-audit -r requirements.txt
```

## Author

**Firas Obeida**

Computer Engineer | Software Engineering | DevOps | AI/ML | Embedded Systems

GitHub: https://github.com/FirasObieda
