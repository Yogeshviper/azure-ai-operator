FROM python:3.11-slim



# Install system dependencies

RUN apt-get update && apt-get install -y gcc build-essential \

    && rm -rf /var/lib/apt/lists/*


# Set working directory

WORKDIR /app


# Copy requirements first (better layer caching)

COPY requirements.txt .


# Upgrade pip and install dependencies

RUN pip install --upgrade pip \

    && pip install --no-cache-dir -r requirements.txt


# Copy source code

COPY src ./src


# Create non-root user

RUN useradd -m appuser

RUN mkdir -p /app/.files && chown -R appuser:appuser /app

USER appuser


# Expose port

EXPOSE 8000


# Start Chainlit

CMD ["python", "-m", "chainlit", "run", "src/chainlit_app.py", "--host", "0.0.0.0", "--port", "8000"]

