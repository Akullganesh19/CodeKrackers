# ─────────────────────────────────────────────────────────────────────
# Nitro Enclave Dockerfile
# 
# This builds the container image that will be converted into an
# Enclave Image File (EIF) via `nitro-cli build-enclave`.
# 
# The resulting EIF runs INSIDE the Nitro Enclave with:
#   - No network access (only vsock to parent EC2 instance)
#   - No persistent disk access
#   - No shell or SSH access
#   - Hardware-encrypted memory
#   - Attestation support via nitro-cli
# 
# Build for enclave:
#   nitro-cli build-enclave --docker-uri vas-enclave:latest --output-file vas-enclave.eif
# 
# Run enclave:
#   nitro-cli run-enclave --eif-path vas-enclave.eif --memory 2048 --cpu-count 2
# 
# The enclave automatically starts the vsock server on port 5000,
# listening for encrypted detection requests from the parent host.
# ─────────────────────────────────────────────────────────────────────

FROM python:3.11-slim-bookworm AS enclave-base

# ─── Nitro Enclave has no network access — install packages offline
# During Docker build, we have access to the internet.
# Inside the enclave, the container is purely filesystem + vsock.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# ─── Install system dependencies for ML inference ──────────────
# scikit-learn and numpy need libgomp for threaded operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python dependencies ──────────────────────────────
# We install transformers + torch for production ML inference.
# For memory-constrained enclaves, these can be commented out
# and the keyword fallback classifier will be used instead.
COPY backend/enclave/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ─── ML Model Weights (loaded into enclave memory at boot) ────
# The model directory is baked into the EIF so no external access is needed.
# In production, train a lightweight DistilBERT model and place it here.
COPY backend/enclave/models/ /app/models/

# ─── Copy the enclave server code ─────────────────────────────
COPY backend/enclave/enclave_server.py /app/enclave_server.py

# ─── nitro-cli (required for attestation) ─────────────────────
# The 'nitro-cli' binary is provided by AWS on the host at /usr/bin.
# Inside the enclave, we use the Python subprocess to call it.
# Note: nitro-cli is NOT installed inside the enclave container;
# the attestation mechanism uses a built-in Nitro hypervisor call.

# ─── Runtime ───────────────────────────────────────────────────
# The enclave server listens on vsock port 5000.
# vsock is the ONLY communication channel — no TCP/IP stack.
EXPOSE 5000

CMD ["python", "-u", "enclave_server.py"]