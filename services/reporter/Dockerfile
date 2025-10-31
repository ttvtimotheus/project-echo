FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# starte über Python, liest $PORT aus der Umgebung
CMD ["python","main.py"]
