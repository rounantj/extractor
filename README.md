# 🖼️ Extractor de Imagens de Produto

API FastAPI para extrair as 15 melhores imagens de produtos de e-commerce usando Selenium headless.

## 🚀 Funcionalidades

- ✅ **Detecção automática** de lojas (Amazon, Mercado Livre, AliExpress, etc.)
- ✅ **Filtros inteligentes** para imagens de produto (remove ícones, logos, estrelas)
- ✅ **Ordenação por qualidade** baseada em tamanho real e resolução
- ✅ **Top 15 imagens** ordenadas da melhor para pior qualidade
- ✅ **Modo headless** (sem interface gráfica) - perfeito para servidores
- ✅ **Suporte a múltiplas lojas** com padrões específicos

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **Selenium** - Automação de navegador headless
- **Chrome WebDriver** - Navegador sem interface gráfica
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## 📦 Instalação

### Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
python main.py
```

### Heroku

```bash
# Fazer deploy
heroku create seu-app-nome
git add .
git commit -m "Initial commit"
git push heroku main
```

## 🎯 Uso da API

### Endpoint Principal

**POST** `/extract-images`

### Exemplo de Request

```json
{
  "url": "https://www.amazon.com.br/produto-exemplo",
  "store_name": "Amazon" // Opcional - será detectado automaticamente
}
```

### Exemplo de Response

```json
{
  "store_name": "Amazon",
  "url": "https://www.amazon.com.br/produto-exemplo",
  "total_images_found": 25,
  "top_15_images": [
    {
      "url": "https://m.media-amazon.com/images/I/81wQj-jVThL._AC_SX679_.jpg",
      "alt": "Descrição da imagem",
      "title": "",
      "width": "651",
      "height": "700",
      "quality_score": 90.89,
      "file_size_mb": 0.08
    }
  ],
  "extraction_method": "selenium_headless_product_only"
}
```

## 🌐 Lojas Suportadas

- **Amazon** - `amazon.com.br`, `amazon.com`
- **Mercado Livre** - `mercadolivre.com.br`, `mlstatic.com`
- **AliExpress** - `aliexpress.com`, `alicdn.com`
- **Americanas** - `americanas.com.br`, `vtexassets.com`
- **Casas Bahia** - `casasbahia.com.br`
- **Shopee** - `shopee.com.br`
- **Shein** - `shein.com`, `ltwebstatic.com`

## 🔧 Configuração

### Variáveis de Ambiente

- `PORT` - Porta do servidor (Heroku define automaticamente)
- `CHROME_BIN` - Caminho para o Chrome (opcional)

### Configurações do Chrome

O Chrome é configurado automaticamente para:

- Modo headless (sem interface gráfica)
- Anti-detecção de automação
- User agent realista
- Otimizações para servidor

## 📊 Como Funciona

1. **Recebe URL** do produto
2. **Detecta automaticamente** a loja
3. **Abre página** com Selenium headless
4. **Aguarda carregamento** de JavaScript
5. **Extrai imagens** com filtros rigorosos
6. **Calcula scores** de qualidade
7. **Ordena** da melhor para pior
8. **Retorna top 15** imagens

## 🚀 Deploy no Heroku

### 1. Criar app

```bash
heroku create seu-app-nome
```

### 2. Configurar buildpacks

```bash
heroku buildpacks:add heroku/google-chrome
heroku buildpacks:add heroku/chromedriver
heroku buildpacks:add heroku/python
```

### 3. Fazer deploy

```bash
git push heroku main
```

### 4. Verificar logs

```bash
heroku logs --tail
```

## 🔍 Endpoints

- **GET** `/` - Informações da API
- **POST** `/extract-images` - Extrair imagens de produto
- **GET** `/health` - Health check

## 📝 Exemplo de Uso com cURL

```bash
curl -X POST "http://localhost:4000/extract-images" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com.br/Lanterna-Recarregavel/dp/B0DKWV28CZ"
  }'
```

## ⚠️ Limitações

- Requer Chrome/Chromedriver no servidor
- Pode ser bloqueado por algumas lojas
- Tempo de resposta depende da velocidade da página
- Algumas lojas podem ter proteções anti-bot

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
