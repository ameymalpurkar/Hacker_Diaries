FROM python:3.11-slim

# Set critical environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1

# Create and set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (Make sure .gitignore rules are respected)
COPY . .

# Start a background sleep process to keep the container alive indefinitely.
# This allows you to SSH/Shell into the Render container and run `python journal_cli.py secret`
CMD ["tail", "-f", "/dev/null"]
