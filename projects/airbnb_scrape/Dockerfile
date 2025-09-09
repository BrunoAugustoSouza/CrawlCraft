# Usar uma imagem oficial do Python
FROM python:3.11-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

RUN mkdir -p /app/data

RUN mkdir -p /app/data/sql

RUN mkdir -p /app/data/jsons

# Copiar requirements.txt e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código (inclusive a pasta src)
COPY . .

EXPOSE 5000

# Comando para rodar o script principal dentro da pasta src
# substitua "main.py" pelo nome do seu script
# Instalar Playwright e os browsers
RUN pip install playwright && playwright install --with-deps

CMD ["python", "src/app.py"]