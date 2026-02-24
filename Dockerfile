FROM python:3.11-slim-bookworm

# Install basic tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Default command
CMD ["tail", "-f", "/dev/null"]
