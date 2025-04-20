FROM python:3.13

WORKDIR /app

# Copy requirements.txt
COPY djangoProjectTask3/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the project
COPY djangoProjectTask3/ /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
