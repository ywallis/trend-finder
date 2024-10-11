# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install cron and other dependencies
RUN apt-get update && apt-get install -y cron

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add the cron job (using `python`)
RUN echo "*/10 * * * * /usr/local/bin/python /usr/src/app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job

# Give execution rights to the cron job file
RUN chmod 0644 /etc/cron.d/my-cron-job

# Apply the cron job to the crontab
RUN crontab /etc/cron.d/my-cron-job

# Create the log file to be used by cron
RUN touch /var/log/cron.log

# Start cron in the foreground
CMD cron && tail -f /var/log/cron.log
