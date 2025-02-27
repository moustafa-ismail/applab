# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the Streamlit port
EXPOSE 8088

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8088", "--server.address=0.0.0.0"]
