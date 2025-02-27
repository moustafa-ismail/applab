# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 8501

# Run the Flask app
ENTRYPOINT ["python", "flask_app.py", "--port=8501"]
