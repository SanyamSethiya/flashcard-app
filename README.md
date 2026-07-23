# Recall — Spaced Repetition Flashcard App

Recall is a two-tier web application that helps you actually remember what
you study. Instead of reviewing every flashcard every day, it uses a
simplified **SM-2 spaced-repetition algorithm** to calculate exactly when
you're about to forget something — and shows you that card at that moment.
No cramming, no wasted reviews.

The project is fully containerized with **Docker**, deployed through a
**Jenkins CI/CD pipeline**, and runs on **AWS EC2** across two separate
instances (a Jenkins master and an app worker), following real DevOps
separation-of-concerns practice.

---

## Demo

Run locally in under a minute:
```bash
git clone https://github.com/yourusername/flashcard-app.git
cd flashcard-app
cp .env.example .env
docker compose up --build
```
Then open **http://localhost:5000**

---

## Table of Contents

- [Tools Explored](#tools-explored)
- [Project Structure](#project-structure)
- [How the Spaced Repetition Algorithm Works](#how-the-spaced-repetition-algorithm-works)
- [Features](#features)
- [Run Locally](#run-locally)
- [CI/CD Pipeline (Jenkins)](#cicd-pipeline-jenkins)
- [Deployment Guide — AWS EC2 (2-Instance Setup)](#deployment-guide--aws-ec2-2-instance-setup)
- [Environment Variables](#environment-variables)
- [Health Check](#health-check)
- [Contribution Guidelines](#contribution-guidelines)
- [Support](#support)

---

## Tools Explored

🛠️ **Stack & Tools:**
- **Flask** (Python) — backend + server-rendered frontend
- **MySQL 8.0** — relational database
- **Gunicorn** — production WSGI server
- **Docker & Docker Compose** — containerization and orchestration
- **Jenkins** — CI/CD automation (build → push → deploy)
- **Docker Hub** — container registry
- **GitHub Webhooks** — automatic pipeline triggers on push
- **AWS EC2** — two-instance deployment (Jenkins master + app worker)

🚢 **High-Level Overview:**
- Two-tier architecture: app container (Flask) + data container (MySQL)
- Jenkins master builds and pushes Docker images, then deploys remotely over SSH
- App worker instance runs the live containers via `docker compose`
- GitHub webhook triggers a fresh build + deploy automatically on every push
- Self-healing database schema — missing tables are created automatically on startup


## Project Structure

```
flashcard-app/
├── backend/
│   ├── app.py                  # Flask routes + self-healing DB schema check
│   ├── spaced_repetition.py    # SM-2 scheduling logic
│   ├── requirements.txt
│   └── Dockerfile              # Gunicorn, non-root user
├── frontend/
│   ├── templates/              # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css       # Design + animations
│       └── js/script.js        # Flip-card + toast interactions
├── database/
│   └── init.sql                # MySQL schema + seed data
├── jenkins/
│   └── Jenkinsfile             # CI/CD pipeline definition
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## How the Spaced Repetition Algorithm Works

Every card tracks `repetitions`, `ease_factor`, and `interval_days`. After
each review, you rate how well you remembered it:

| Rating | Effect |
|---|---|
| **Again** | Forgot completely — progress resets, card returns **tomorrow** |
| **Hard** | Struggled — ease factor drops slightly, card comes back **more often** |
| **Good** | Remembered normally — interval grows steadily (1 → 6 → ~15 → ~37 days...) |
| **Easy** | Effortless — ease factor increases, card comes back **later and less often** |

A new card's **first review is always fixed at tomorrow**, regardless of
rating (as long as it isn't "Again"). From the second review onward, your
rating controls the pace — cards you know well drift weeks or months into
the future; cards you struggle with keep resurfacing daily.

---

## Features

- Add / **edit** / **delete** flashcards
- Spaced-repetition review flow with a flip-card animation
- **Category filter** on the dashboard
- **Mastery progress bar** per card (based on ease factor)
- **Due-today status dot** on each card
- **Review streak counter** (consecutive days reviewed)
- **Toast notifications** on add/edit/delete
- Flippable hero card on the homepage + "How Recall Works" explainer section
- Self-healing database schema (auto-creates missing tables on startup)

---

## Run Locally

```bash
git clone https://github.com/yourusername/flashcard-app.git
cd flashcard-app
cp .env.example .env
docker compose up -d --build
```

App available at **http://localhost:5000**

Check container status:
```bash
docker ps
docker compose logs -f
```

Stop everything:
```bash
docker compose down
```

---

## CI/CD Pipeline (Jenkins)

The Jenkinsfile defines a 6-stage pipeline:

1. **Checkout** — pulls latest code from GitHub
2. **Build Docker Image** — builds the Flask app image
3. **Login to Docker Hub** — authenticates using stored credentials
4. **Push Image** — pushes tagged + `latest` images to Docker Hub
5. **Deploy to AWS EC2** — SSHes into the app worker, pulls latest code + image, restarts containers
6. **Health Check** — verifies `/health` returns a healthy response

**Required Jenkins credentials** (Manage Jenkins → Credentials):

| ID | Kind | Purpose |
|---|---|---|
| `dockerhub-credentials` | Username with password | Docker Hub login (use an Access Token, not your password) |
| `aws-ec2-ssh-key` | SSH Username with private key | SSH access to the app worker (username: `ubuntu`) |
| `aws-ec2-host` | Secret text | `ubuntu@<WORKER_PUBLIC_IP>` |

**GitHub Webhook** (for automatic builds on every push):
- Payload URL: `http://<JENKINS_MASTER_IP>:8080/github-webhook/`
- Content type: `application/json`
- Events: **Just the push event**

---

## Deployment Guide — AWS EC2 (2-Instance Setup)

This project intentionally separates CI/CD from the running application —
a Jenkins **master** instance and a separate app **worker** instance —
rather than running everything on one box.

### Instance 1: App Worker
1. Launch Ubuntu 22.04 EC2 (`t2.medium`), open ports `22`, `5000`, `3306` (optional)
2. Install Docker + Docker Compose + Git
3. Clone this repo, create `.env` with real values
4. Run `docker compose up -d --build` once manually to confirm it works

### Instance 2: Jenkins Master
1. Launch Ubuntu 22.04 EC2 (`t2.medium`), open ports `22`, `8080`
2. Install Docker, Java 17, Jenkins
3. Complete Jenkins setup wizard, install `Docker Pipeline` + `SSH Agent` plugins
4. Add the 3 credentials listed above
5. Allow the worker's security group to accept SSH from the master's IP
6. Create a Pipeline job pointing to this repo's `jenkins/Jenkinsfile`
7. Add the GitHub webhook

Once both are set up, every `git push` to `main` automatically triggers a
full build → push → deploy cycle with zero manual steps.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in real values — this file is
gitignored and never committed:

```
DB_USER=your_user
DB_PASSWORD=your_strong_password_here
DB_NAME=flashcards_db
```

---

## Health Check

The app exposes a health endpoint used by the CI/CD pipeline and can be
checked manually:
```bash
curl http://<WORKER_PUBLIC_IP>:5000/health
```
Expected response:
```json
{"status": "healthy"}
```

---

## Contribution Guidelines

1. Fork the repository and create a feature branch
2. Make your changes, following the existing code style
3. Test locally with `docker compose up --build`
4. Submit a Pull Request with a clear description of your changes

---

## Support

For questions or issues, please open an issue in this repository.
