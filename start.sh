#!/bin/bash

echo "🚀 Iniciando Extractor de Imagens API..."
echo "========================================"

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python 3.9+"
    exit 1
fi

# Instalar dependências se necessário
echo "🔧 Instalando dependências..."
pip3 install -r requirements.txt

# Verificar se o Chrome está disponível
echo "🌐 Verificando Chrome..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome não encontrado. A API pode não funcionar corretamente."
    echo "   Para instalar no Ubuntu/Debian: sudo apt install google-chrome-stable"
    echo "   Para instalar no macOS: brew install --cask google-chrome"
fi

# Iniciar a API
echo "🔥 Iniciando API na porta 4000..."
echo "   📍 Endpoint: http://localhost:4000"
echo "   📍 Docs: http://localhost:4000/docs"
echo "   📍 Health: http://localhost:4000/health"
echo ""
echo "⏹️  Para parar: Ctrl+C"
echo ""

python3 main.py
