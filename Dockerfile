# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# Stage 1: Builder (Compiles dependencies)
# -----------------------------------------------------------------------------
    ARG PYTHON_VERSION=3.12
    FROM python:${PYTHON_VERSION}-slim-bookworm as builder
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Install build dependencies (compilers, etc.)
    # We clean up apt lists immediately to keep layers small
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        musl-dev \
        python3-dev \
        libffi-dev \
        # Add any other build-time libraries here
        && rm -rf /var/lib/apt/lists/*
    
    # Install python dependencies into a temporary directory
    COPY requirements.txt .
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # -----------------------------------------------------------------------------
    # Stage 2: Runner (Final Runtime Image)
    # -----------------------------------------------------------------------------
    FROM python:${PYTHON_VERSION}-slim-bookworm as runner
    
    # Security: Create a non-root user
    ARG UID=10001
    RUN adduser \
        --disabled-password \
        --gecos "" \
        --home "/nonexistent" \
        --shell "/sbin/nologin" \
        --no-create-home \
        --uid "${UID}" \
        appuser
    
    WORKDIR /app
    
    # Install ONLY runtime dependencies
    # curl/gnupg needed for Doppler; libpq5 needed for Postgres
    RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        libpq5 \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Doppler CLI (Optimized for Debian/Slim)
    RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg \
        && echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" > /etc/apt/sources.list.d/doppler-cli.list \
        && apt-get update \
        && apt-get install -y --no-install-recommends doppler \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy installed python packages from Builder stage
    COPY --from=builder /install /usr/local
    
    # Copy application code
    COPY . .
    
    # Adjust permissions for non-root user
    RUN chown -R appuser:appuser /app
    
    # Switch to non-root user
    USER appuser
    
    # Expose port
    EXPOSE 8000
    
    # Use Doppler to inject secrets into Gunicorn + Uvicorn
    # CMD ["doppler", "run", "--", "gunicorn", "core.asgi:application", \
    #      "-k", "uvicorn.workers.UvicornWorker", \
    #      "--bind", "0.0.0.0:8000", \
    #      "--workers", "4", \
    #      "--access-logfile", "-", \
    #      "--error-logfile", "-"]

    CMD ["doppler", "run", "--", "sh", "-c", "python manage.py collectstatic --noinput && gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]