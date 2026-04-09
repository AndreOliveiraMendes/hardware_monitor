FROM python:3.11-slim

WORKDIR /app

# dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app
COPY app.py .
COPY templates/ /app/templates/ 

# garantir pasta do banco
RUN mkdir -p /app/data

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
