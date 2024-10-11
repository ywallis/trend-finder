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
RUN echo "0 10,22 * * * root /usr/local/bin/python /usr/src/app/main.py" > /etc/cron.d/my-cron-job

# Give execution rights to the cron job file
RUN chmod 0644 /etc/cron.d/my-cron-job

# Start cron in the foreground
CMD ["cron", "-f"]
