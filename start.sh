#!/bin/bash

# Script de inicialização otimizado para Heroku
echo "🚀 Iniciando Image Extractor API..."

# Configurar variáveis de ambiente para o Chrome (SOLUÇÃO COMPROVADA)
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
export GOOGLE_CHROME_SHIM=/app/.apt/usr/bin/google-chrome

# SOLUÇÃO COMPROVADA: Limpar diretórios temporários existentes
echo "🧹 Limpando diretórios temporários existentes..."
find /tmp -name "chrome-*" -type d -exec rm -rf {} + 2>/dev/null || true
find /tmp -name "chromium-*" -type d -exec rm -rf {} + 2>/dev/null || true

# SOLUÇÃO COMPROVADA: Criar diretório temporário limpo
mkdir -p /tmp/chrome-temp
chmod 755 /tmp/chrome-temp

# SOLUÇÃO COMPROVADA: Verificar se o Chrome está disponível
if [ -f "$CHROME_BIN" ]; then
    echo "✅ Chrome encontrado em: $CHROME_BIN"
    echo "🔧 Versão do Chrome:"
    $CHROME_BIN --version
else
    echo "⚠️ Chrome não encontrado em $CHROME_BIN"
    echo "🔍 Procurando em outros locais..."
    find /usr -name "google-chrome*" 2>/dev/null || echo "Chrome não encontrado"
fi

# SOLUÇÃO COMPROVADA: Verificar se o Chromedriver está disponível
if [ -f "$CHROMEDRIVER_PATH" ]; then
    echo "✅ Chromedriver encontrado em: $CHROMEDRIVER_PATH"
    echo "🔧 Versão do Chromedriver:"
    $CHROMEDRIVER_PATH --version
else
    echo "⚠️ Chromedriver não encontrado em $CHROMEDRIVER_PATH"
    echo "🔍 Procurando em outros locais..."
    find /usr -name "chromedriver*" 2>/dev/null || echo "Chromedriver não encontrado"
fi

# Iniciar a aplicação
echo "✅ Iniciando FastAPI..."
exec uvicorn main:app --host=0.0.0.0 --port=$PORT --workers=1
