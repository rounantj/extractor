# Image Extractor API

API para extrair imagens de produtos de e-commerce usando estratégia híbrida (Selenium + Requests).

## 🚀 Principais Melhorias para Heroku

### ✅ Problemas Resolvidos
- **Conflitos de diretório**: Removido `--user-data-dir` que causava erros no Heroku
- **Estratégia de fallback**: Implementado sistema robusto com requests + BeautifulSoup
- **Limpeza de recursos**: Chrome é fechado adequadamente após cada uso
- **Configuração otimizada**: Chrome configurado especificamente para ambiente containerizado

### 🔧 Estratégia Híbrida
1. **Primeira tentativa**: Selenium Chrome headless (mais robusto)
2. **Fallback automático**: Requests + BeautifulSoup se Selenium falhar
3. **Garantia de funcionamento**: Pelo menos uma estratégia sempre funcionará

### 📦 Dependências Atualizadas
- `beautifulsoup4==4.12.2` - Para parsing HTML no fallback
- `selenium==4.35.0` - Para navegação headless
- `fastapi==0.104.1` - Framework da API

## 🏗️ Estrutura do Projeto

```
extractor/
├── main.py                 # API FastAPI principal
├── image_extractor.py      # Lógica de extração híbrida
├── chrome_config.py        # Configurações específicas do Heroku
├── start.sh               # Script de inicialização otimizado
├── Procfile               # Configuração do Heroku
├── requirements.txt       # Dependências Python
└── runtime.txt            # Versão do Python
```

## 🚀 Como Usar

### Endpoint Principal
```bash
POST /extract-images
{
    "url": "https://www.kabum.com.br/produto/...",
    "store_name": "Kabum"  # opcional
}
```

### Exemplo de Resposta
```json
{
    "store_name": "Kabum",
    "url": "https://www.kabum.com.br/produto/...",
    "total_images_found": 15,
    "top_15_images": [...],
    "extraction_method": "selenium_headless"
}
```

## 🔧 Configuração do Heroku

### Variáveis de Ambiente
```bash
CHROME_BIN=/usr/bin/google-chrome
CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
```

### Buildpacks Necessários
1. `heroku/python` - Runtime Python
2. `heroku/google-chrome` - Chrome headless
3. `heroku/chromedriver` - Driver do Chrome

## 📊 Métricas de Qualidade

A API calcula automaticamente scores de qualidade para cada imagem baseado em:
- Tamanho real do arquivo
- Dimensões HTML
- Padrões específicos da loja
- Extensão do arquivo
- Texto alternativo

## 🛡️ Tratamento de Erros

- **Timeout**: Fallback automático para requests
- **Chrome falha**: Fallback para BeautifulSoup
- **Limpeza automática**: Recursos são liberados após cada uso
- **Logs detalhados**: Rastreamento completo de cada operação

## 🔄 Deploy

```bash
# Fazer commit das mudanças
git add .
git commit -m "feat: implementa estratégia híbrida para Heroku"

# Deploy para Heroku
git push heroku main
```

## 📈 Performance

- **Selenium**: ~5-10 segundos (mais preciso)
- **Requests**: ~2-5 segundos (mais rápido)
- **Fallback automático**: Sempre funcional
- **Memória otimizada**: Limpeza automática de recursos

## 🎯 Lojas Suportadas

- Amazon
- Mercado Livre
- AliExpress
- Americanas
- Casas Bahia
- Shopee
- Shein
- Kabum
- Generic (outras lojas)

## 🚨 Troubleshooting

### Erro: "session not created: probably user data directory is already in use"
- ✅ **RESOLVIDO**: Removido `--user-data-dir` das configurações
- ✅ **RESOLVIDO**: Implementada limpeza automática de arquivos temporários

### Erro: "Chrome não inicia no Heroku"
- ✅ **RESOLVIDO**: Configurações otimizadas para ambiente containerizado
- ✅ **RESOLVIDO**: Fallback automático para requests + BeautifulSoup

### Erro: "Timeout ao carregar página"
- ✅ **RESOLVIDO**: Fallback automático para método mais rápido
- ✅ **RESOLVIDO**: Múltiplas estratégias de extração
