# Multi-stage build for stock analysis environment
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # sudo 패키지를 설치합니다.
    sudo \
    python3 \
    python3-pip \
    python3-venv \
    vim \
    git \
    # uv installation dependencies
    curl \
    # Korean fonts for chart visualization
    fonts-nanum \
    fonts-nanum-coding \
    fonts-nanum-extra \
    # Additional system tools
    make \
    # Build tools for Python packages
    gcc \
    g++ \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# python3를 위한 venv, pipx를 설치하고, yfinance, pandas 등을 미리 설치합니다.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install pipx yfinance pandas openpyxl numpy seaborn matplotlib openai python-dotenv googletrans uv

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Create user with same UID/GID as host user (will be overridden at build time)
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER_NAME=stockuser

# Create group and user with specified IDs
RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to user
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

# Install uv for user
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/${USER_NAME}/.cargo/bin:$PATH"

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create workspace directory
RUN mkdir -p /home/${USER_NAME}/workspace

# Set working directory for mounted volumes
WORKDIR /home/${USER_NAME}/workspace

# Default command
CMD ["/bin/bash"]
