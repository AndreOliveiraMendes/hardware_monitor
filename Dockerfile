FROM python:3.11-slim

WORKDIR /app

# dependências
COPY requirements.txt .
RUN python -m pip install --root-user-action=ignore --no-cache-dir --upgrade pip && \
    pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

# app
COPY . .

# pasta de dados
RUN mkdir -p /app/data

# entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
