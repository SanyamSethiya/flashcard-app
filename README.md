# Recall — Spaced Repetition Flashcard App

A two-tier web app that schedules flashcard reviews using a simplified SM-2
spaced-repetition algorithm, containerized with Docker, deployed via a
Jenkins CI/CD pipeline to AWS.

## Architecture (Two-Tier)

```
┌─────────────────────────────┐      ┌──────────────────┐
│   Container 1: web          │      │  Container 2:     │
│   Flask (frontend+backend)  │ ───► │  mysql_db (MySQL) │
│   Port 5000                 │      │  Port 3306         │
└─────────────────────────────┘      └──────────────────┘
```

## Project Structure

```
flashcard-app/
├── backend/
│   ├── app.py                  # Flask routes
│   ├── spaced_repetition.py    # SM-2 scheduling logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── templates/               # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css        # Design + animations
│       └── js/script.js         # Flip-card interaction
├── database/
│   └── init.sql                 # MySQL schema + seed data
├── jenkins/
│   └── Jenkinsfile              # CI/CD pipeline
├── docker-compose.yml
└── .env.example
```

## Run Locally

```bash
cd flashcard-app
docker compose up --build
```

App available at: **http://localhost:5000**

## Features

- Add / **edit** / **delete** flashcards
- Spaced-repetition review flow with a flip-card animation
- **Category filter** on dashboard
- **Mastery progress bar** per card (based on ease factor)
- **Due-today status dot** on each card
- **Review streak counter** (consecutive days reviewed)
- **Toast notifications** on add/edit/delete
- Flippable hero card on the homepage + "How Recall Works" explainer section

## How the Algorithm Works

Every card has `repetitions`, `ease_factor`, and `interval_days`. After each
review, the user rates recall quality (Again / Hard / Good / Easy). Based on
that rating, `spaced_repetition.py` recalculates the next review date —
cards you know well get pushed weeks/months out; cards you forget come back
tomorrow.

## CI/CD Flow (Jenkins)

1. Checkout code from Git
2. Build Docker image from `backend/Dockerfile`
3. Push image to Docker Hub
4. SSH into AWS EC2, pull latest image, restart via `docker compose`
5. Health check on `/health` endpoint

**Before running the pipeline**, set these Jenkins credentials:
- `dockerhub-credentials` — Docker Hub username/password
- `aws-ec2-host` — EC2 SSH connection string
- `aws-ec2-ssh-key` — SSH private key for EC2 access

## Next Steps for AWS Deployment

- Launch an EC2 instance, install Docker + Docker Compose
- Open inbound port 5000 (and 3306 if MySQL needs external access) in the security group
- Copy `docker-compose.yml` and `database/init.sql` to the EC2 instance
- Point the Jenkinsfile's `AWS_EC2_HOST` to that instance
