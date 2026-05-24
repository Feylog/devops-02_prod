# syntax=docker/dockerfile:1.7

# ---- Builder stage: install deps into an isolated venv ----
FROM python:3.12-slim AS builder

# System deps needed only at build time (compiling cryptography wheels etc.).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create the virtual environment in a known location.
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python deps. Copy requirements.txt first so Docker can cache
# the pip install layer when only app code changes.
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ---- Runtime stage: minimal image with just the venv + app code ----
FROM python:3.12-slim AS runtime

# Create a non-root user. UID 10001 is a convention some k8s
# admission controllers expect (any high UID works).
RUN groupadd --system --gid 10001 app && \
    useradd  --system --uid 10001 --gid app --no-create-home app

# Copy the populated venv from the builder stage.
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# App code lives here. /app is owned by the app user.
WORKDIR /app
COPY --chown=app:app alembic.ini .
COPY --chown=app:app app/ ./app/

# Run as the unprivileged user.
USER app

# Document the port the app listens on (metadata only; doesn't publish).
EXPOSE 8000

# Healthcheck: hits /healthz. Container is unhealthy if liveness fails.
# Curl is not installed in slim images, so we use python directly.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; \
        sys.exit(0) if urllib.request.urlopen('http://localhost:8000/healthz', timeout=2).status == 200 else sys.exit(1)" \
    || exit 1

# Production-shaped command. --workers tunes process count; for local
# dev we'll override this in docker-compose.yml to use --reload instead.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
