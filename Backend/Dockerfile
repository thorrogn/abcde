# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the application dependencies file to the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port that the Flask application listens on
EXPOSE 5050

# Set environment variables (if needed, can also be passed during runtime)
ENV FLASK_APP=file.py
# Add this line to disable debug mode for production
ENV FLASK_DEBUG=0

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]
