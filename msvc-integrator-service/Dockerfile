FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /var/log/flask

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "src.app:app"]
