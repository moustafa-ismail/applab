# Use Microsoft Dev Containers Python base image
FROM mcr.microsoft.com/devcontainers/python:3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit default port
EXPOSE 8088

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8088", "--server.address=0.0.0.0"]
