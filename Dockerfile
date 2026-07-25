# Imagem base do Python
FROM python:3.10-slim

# Instalar dependências do sistema para Selenium e PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    wget \
    unzip \
    chromium-driver \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho no contêiner
WORKDIR /app

# Copiar o requirements.txt para o contêiner
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código-fonte para o contêiner
COPY src/ .

# Comando padrão para execução
CMD ["python", "runner.py"]
