FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
# Copy frontend code (templates + static) - Flask serves these directly
COPY frontend/ ./frontend/

# Create a non-root user (security best practice - don't run as root in production)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

EXPOSE 5000

# Gunicorn: production WSGI server (replaces Flask's dev server)
# -w 4 = 4 worker processes, -b = bind address, --timeout = kill hung requests after 60s
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "60", "app:app"]
