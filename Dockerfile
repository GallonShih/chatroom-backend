# Dockerfile

FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

# Expose port 8000
EXPOSE 8000

CMD ["python", "main.py"]
