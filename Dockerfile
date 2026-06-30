FROM python:3.11-slim

# Set critical environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1
ENV PORT=10000

# Create and set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Start a dummy HTTP server on the required PORT to satisfy Render's Web Service health check.
# This keeps the container alive for free. You can then use the Render Shell to run your CLI.
CMD python -m http.server $PORT
