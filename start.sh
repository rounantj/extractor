#!/bin/bash

# Script de inicialização otimizado para Heroku
echo "🚀 Iniciando Image Extractor API..."

# Configurar variáveis de ambiente para o Chrome
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Limpar diretórios temporários se existirem
if [ -d "/tmp/chrome-data" ]; then
    echo "🧹 Limpando diretórios temporários..."
    rm -rf /tmp/chrome-data
fi

# Criar diretório temporário limpo
mkdir -p /tmp/chrome-temp

# Iniciar a aplicação
echo "✅ Iniciando FastAPI..."
exec uvicorn main:app --host=0.0.0.0 --port=$PORT --workers=1
