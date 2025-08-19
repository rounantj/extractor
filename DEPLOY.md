# 🚀 Guia de Deploy para Heroku

## 📋 Pré-requisitos

1. **Conta no Heroku** - [heroku.com](https://heroku.com)
2. **Heroku CLI** instalado
3. **Git** configurado
4. **Chrome/Chromedriver** (será instalado automaticamente)

## 🔧 Passo a Passo

### 1. Login no Heroku

```bash
heroku login
```

### 2. Criar novo app

```bash
heroku create seu-app-nome
```

### 3. Configurar buildpacks (IMPORTANTE!)

```bash
# Adicionar buildpacks na ordem correta
heroku buildpacks:add heroku/google-chrome
heroku buildpacks:add heroku/chromedriver
heroku buildpacks:add heroku/python
```

### 4. Verificar buildpacks

```bash
heroku buildpacks
```

### 5. Fazer deploy

```bash
git add .
git commit -m "Initial commit"
git push heroku main
```

### 6. Verificar logs

```bash
heroku logs --tail
```

### 7. Abrir app

```bash
heroku open
```

## 🌐 URLs da API

Após o deploy, sua API estará disponível em:

- **API**: `https://seu-app-nome.herokuapp.com`
- **Docs**: `https://seu-app-nome.herokuapp.com/docs`
- **Health**: `https://seu-app-nome.herokuapp.com/health`

## 📝 Exemplo de Uso

### cURL

```bash
curl -X POST "https://seu-app-nome.herokuapp.com/extract-images" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com.br/produto-exemplo"
  }'
```

### JavaScript

```javascript
const response = await fetch(
  "https://seu-app-nome.herokuapp.com/extract-images",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: "https://www.amazon.com.br/produto-exemplo",
    }),
  }
);

const result = await response.json();
console.log(result.top_15_images);
```

### Python

```python
import requests

response = requests.post(
    'https://seu-app-nome.herokuapp.com/extract-images',
    json={
        'url': 'https://www.amazon.com.br/produto-exemplo'
    }
)

result = response.json()
print(f"Encontradas {len(result['top_15_images'])} imagens")
```

## ⚠️ Problemas Comuns

### 1. Chrome não encontrado

```bash
# Verificar buildpacks
heroku buildpacks

# Reinstalar se necessário
heroku buildpacks:clear
heroku buildpacks:add heroku/google-chrome
heroku buildpacks:add heroku/chromedriver
heroku buildpacks:add heroku/python
```

### 2. Timeout na primeira requisição

- A primeira requisição pode demorar (cold start)
- Use o endpoint `/health` para "aquecer" a API

### 3. Erro de memória

```bash
# Verificar logs
heroku logs --tail

# Aumentar dyno se necessário
heroku ps:scale web=1:standard-1x
```

## 🔍 Monitoramento

### Logs em tempo real

```bash
heroku logs --tail
```

### Status da aplicação

```bash
heroku ps
```

### Métricas

```bash
heroku addons:open scout
```

## 💰 Custos

- **Hobby Dyno**: Gratuito (30 min/dia)
- **Basic Dyno**: $7/mês (24/7)
- **Standard Dyno**: $25/mês (melhor performance)

## 🚀 Otimizações

### 1. Cache Redis

```bash
heroku addons:create heroku-redis:hobby-dev
```

### 2. Monitoramento

```bash
heroku addons:create papertrail:choklad
```

### 3. SSL automático

```bash
heroku certs:auto:enable
```

## 📞 Suporte

- **Documentação**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Status**: [status.heroku.com](https://status.heroku.com)
- **Comunidade**: [help.heroku.com](https://help.heroku.com)
