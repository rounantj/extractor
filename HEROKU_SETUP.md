# 🚀 Configuração do Heroku para Image Extractor API

## 📋 Pré-requisitos

1. **Heroku CLI instalado**
2. **Git configurado**
3. **Acesso ao app no Heroku**

## 🔧 Configuração dos Buildpacks

### Passo 1: Verificar buildpacks atuais
```bash
heroku buildpacks --app SEU-APP-NAME
```

### Passo 2: Remover buildpacks existentes (se houver)
```bash
heroku buildpacks:clear --app SEU-APP-NAME
```

### Passo 3: Adicionar buildpacks na ORDEM CORRETA
```bash
# 1. Google Chrome (deve ser primeiro)
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome --app SEU-APP-NAME

# 2. Chromedriver (deve ser segundo)
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver --app SEU-APP-NAME

# 3. Python (deve ser por último)
heroku buildpacks:add heroku/python --app SEU-APP-NAME
```

### Passo 4: Verificar ordem dos buildpacks
```bash
heroku buildpacks --app SEU-APP-NAME
```

**ORDEM CORRETA:**
1. `heroku/google-chrome`
2. `heroku/chromedriver`  
3. `heroku/python`

## 🌍 Variáveis de Ambiente

### Configurar variáveis automaticamente
```bash
heroku config:set CHROME_BIN=/usr/bin/google-chrome --app SEU-APP-NAME
heroku config:set CHROMEDRIVER_PATH=/usr/local/bin/chromedriver --app SEU-APP-NAME
heroku config:set GOOGLE_CHROME_SHIM=/app/.apt/usr/bin/google-chrome --app SEU-APP-NAME
```

### Verificar variáveis configuradas
```bash
heroku config --app SEU-APP-NAME
```

## 🚀 Deploy

### 1. Fazer commit das mudanças
```bash
git add .
git commit -m "feat: implementa configurações comprovadas do Heroku"
```

### 2. Deploy para Heroku
```bash
git push heroku main
```

### 3. Verificar logs
```bash
heroku logs --tail --app SEU-APP-NAME
```

## 🔍 Troubleshooting

### Erro: "Chrome não encontrado"
```bash
# Verificar se o buildpack do Chrome foi adicionado
heroku buildpacks --app SEU-APP-NAME

# Verificar variáveis de ambiente
heroku config --app SEU-APP-NAME
```

### Erro: "Chromedriver não encontrado"
```bash
# Verificar se o buildpack do Chromedriver foi adicionado
heroku buildpacks --app SEU-APP-NAME

# Verificar se está na ordem correta
heroku buildpacks --app SEU-APP-NAME
```

### Erro: "Buildpack não encontrado"
```bash
# Remover e readicionar buildpacks
heroku buildpacks:clear --app SEU-APP-NAME
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome --app SEU-APP-NAME
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver --app SEU-APP-NAME
heroku buildpacks:add heroku/python --app SEU-APP-NAME
```

## 📊 Verificação de Funcionamento

### 1. Health Check
```bash
curl https://SEU-APP-NAME.herokuapp.com/health
```

### 2. Teste de Extração
```bash
curl -X POST "https://SEU-APP-NAME.herokuapp.com/extract-images" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.kabum.com.br/produto/155321/robo-aspirador-e-passa-pano-kabum-smart-700-5-modos-de-limpeza-mapeamento-a-laser-3d-base-de-carregamento-branco-kbsf006"}'
```

## 🎯 Soluções Comprovadas

### ✅ Configurações que Funcionam no Heroku
- **Buildpacks na ordem correta**
- **Variáveis de ambiente configuradas**
- **Diretórios temporários únicos por processo**
- **Configurações de isolamento do Chrome**
- **Fallback automático para requests + BeautifulSoup**

### ❌ Configurações que NÃO Funcionam
- **Buildpacks na ordem errada**
- **Variáveis de ambiente não configuradas**
- **Diretórios compartilhados entre processos**
- **Configurações padrão do Chrome**

## 📚 Recursos Adicionais

- [Heroku Buildpack Google Chrome](https://github.com/heroku/heroku-buildpack-google-chrome)
- [Heroku Buildpack Chromedriver](https://github.com/heroku/heroku-buildpack-chromedriver)
- [Heroku Python Buildpack](https://github.com/heroku/heroku-buildpack-python)
- [Heroku Selenium Guide](https://devcenter.heroku.com/articles/heroku-ci#selenium)
