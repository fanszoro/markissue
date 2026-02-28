FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY tracker_app.py .
COPY run_tracker.py .
COPY app/ app/

# Expose Streamlit default port
EXPOSE 8505

# Set required environment variables
ENV MARKISSUE_DATA_DIR=LocalStorage

# Command to run the application
CMD ["streamlit", "run", "tracker_app.py", "--server.port", "8505", "--server.address", "0.0.0.0"]
