import time
import json
import re
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests

def detect_store_from_url(url):
    """Detecta automaticamente a loja baseado na URL"""
    url_lower = url.lower()
    
    if 'amazon' in url_lower:
        return 'Amazon'
    elif 'mercadolivre' in url_lower or 'mlstatic.com' in url_lower:
        return 'Mercado Livre'
    elif 'aliexpress' in url_lower:
        return 'AliExpress'
    elif 'americanas' in url_lower:
        return 'Americanas'
    elif 'casasbahia' in url_lower:
        return 'Casas Bahia'
    elif 'shopee' in url_lower:
        return 'Shopee'
    elif 'shein' in url_lower:
        return 'Shein'
    else:
        return 'Generic'

def setup_chrome_driver_with_retry(max_retries=3):
    """Tenta configurar o Chrome com múltiplas tentativas"""
    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentativa {attempt + 1} de {max_retries} para configurar Chrome...")
            
            if attempt == 0:
                # Primeira tentativa: configuração padrão
                driver = setup_chrome_driver_headless()
            elif attempt == 1:
                # Segunda tentativa: configuração alternativa
                driver = setup_chrome_driver_fallback()
            else:
                # Terceira tentativa: configuração ultra-simples
                driver = setup_chrome_driver_ultra_simple()
            
            if driver:
                print(f"✅ Chrome configurado com sucesso na tentativa {attempt + 1}")
                return driver
                
        except Exception as e:
            print(f"❌ Tentativa {attempt + 1} falhou: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Aguardando 2 segundos antes da próxima tentativa...")
                time.sleep(2)
            else:
                print(f"❌ Todas as {max_retries} tentativas falharam")
    
    return None

def setup_chrome_driver_headless():
    """Configura o driver do Chrome em modo headless"""
    chrome_options = Options()
    
    # Gerar diretório único para esta instância
    unique_dir = f"/tmp/chrome-{int(time.time())}-{os.getpid()}"
    
    # Configurações básicas e essenciais
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    
    # Configurações críticas para Heroku - SEM diretórios de usuário
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-background-timer-checking')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    
    # Configurações de memória e performance
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-report-upload')
    
    # Configurações de janela
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    
    # User agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Configurações experimentais
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Diretório único para esta instância
    chrome_options.add_argument(f'--user-data-dir={unique_dir}')
    chrome_options.add_argument(f'--data-path={unique_dir}')
    chrome_options.add_argument(f'--disk-cache-dir={unique_dir}/cache')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Erro ao configurar Chrome headless: {e}")
        return None

def setup_chrome_driver_fallback():
    """Configuração alternativa do Chrome para casos de erro no Heroku"""
    try:
        print("Tentando configuração alternativa do Chrome...")
        chrome_options = Options()
        
        # Gerar diretório único para esta instância
        unique_dir = f"/tmp/chrome-alt-{int(time.time())}-{os.getpid()}"
        
        # Configurações mínimas e essenciais - SEM diretórios de usuário
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-background-timer-checking')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--no-report-upload')
        
        # Configurações de janela
        chrome_options.add_argument('--window-size=1366,768')
        
        # User agent simples
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Diretório único para esta instância
        chrome_options.add_argument(f'--user-data-dir={unique_dir}')
        chrome_options.add_argument(f'--data-path={unique_dir}')
        chrome_options.add_argument(f'--disk-cache-dir={unique_dir}/cache')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Configuração alternativa do Chrome bem-sucedida!")
        return driver
        
    except Exception as e:
        print(f"Erro na configuração alternativa do Chrome: {e}")
        return setup_chrome_driver_ultra_simple()

def setup_chrome_driver_ultra_simple():
    """Configuração ultra-simples do Chrome - última tentativa"""
    try:
        print("Tentando configuração ultra-simples do Chrome...")
        chrome_options = Options()
        
        # Gerar diretório único para esta instância
        unique_dir = f"/tmp/chrome-ultra-{int(time.time())}-{os.getpid()}"
        
        # Apenas o essencial - nada mais
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        
        # User agent básico
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        # Diretório único para esta instância
        chrome_options.add_argument(f'--user-data-dir={unique_dir}')
        chrome_options.add_argument(f'--data-path={unique_dir}')
        
        driver = webdriver.Chrome(options=chrome_options)
        print("Configuração ultra-simples do Chrome bem-sucedida!")
        return driver
        
    except Exception as e:
        print(f"Erro na configuração ultra-simples do Chrome: {e}")
        return None

def wait_for_page_load(driver, timeout=30):
    """Aguarda o carregamento completo da página"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(random.uniform(3, 6))
        return True
    except TimeoutException:
        print("Timeout aguardando carregamento da página")
        return False

def wait_for_images_to_load(driver, timeout=30):
    """Aguarda especificamente pelo carregamento de imagens"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "img[src]")) > 0
        )
        time.sleep(random.uniform(2, 4))
        return True
    except TimeoutException:
        print("Timeout aguardando imagens")
        return False

def get_image_dimensions(url):
    """Obtém o tamanho real da imagem via HEAD request"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            content_length = response.headers.get('content-length', 0)
            return int(content_length) if content_length else 0
        return 0
    except:
        return 0

def is_main_product_image(src, element, store_name):
    """Filtro rigoroso para imagens principais de produto"""
    src_lower = src.lower()
    
    # Verificar se é uma URL válida (http/https)
    if not src.startswith(('http://', 'https://')):
        return False
    
    # Padrões específicos para cada loja
    store_patterns = {
        'Amazon': [
            'images-na.ssl-images-amazon.com/images/',
            'images.amazon.com/images/',
            'm.media-amazon.com/images/',
            'product', 'prod'
        ],
        'Mercado Livre': [
            'http2.mlstatic.com/',
            'http2.mlstatic.com/D_',
            'mlstatic.com/',
            'product', 'produto'
        ],
        'AliExpress': [
            'ae01.alicdn.com/kf/',
            'ae02.alicdn.com/kf/',
            'ae03.alicdn.com/kf/',
            'ae04.alicdn.com/kf/',
            'product', 'prod', 'item'
        ],
        'Americanas': [
            'americanas.vtexassets.com/arquivos/ids/',
            'vtexassets.com/arquivos/ids/',
            'product', 'produto'
        ],
        'Casas Bahia': [
            'casasbahia.com.br/arquivos/ids/',
            'vtexassets.com/arquivos/ids/',
            'product', 'produto'
        ],
        'Shopee': [
            'shopee.com.br/arquivos/',
            'shopee.com.br/images/',
            'product', 'produto'
        ],
        'Shein': [
            'img.ltwebstatic.com/images3_ccc/',
            'sheinm.ltwebstatic.com/pwa_dist/images/',
            'product', 'produto'
        ]
    }
    
    # Padrões de EXCLUSÃO rigorosos
    exclude_patterns = [
        'logo', 'icon', 'sprite', 'banner', 'ad', 'social',
        'favicon', 'avatar', 'profile', 'thumb', 'small',
        'transparent-pixel', 'grey-pixel', 'swatch-image',
        'cr-lightbox', 'review-image', 'community-reviews',
        'attach-accessory', 'button-icon', 'media-cheveron',
        'loading', 'placeholder', 'no-image', 'blank',
        'star', 'rating', 'review', 'coupon', 'discount',
        'arrow', 'chevron', 'close', 'menu', 'hamburger',
        'search', 'filter', 'sort', 'pagination',
        'vlibras', 'accessibility', 'a11y', 'libras'
    ]
    
    # Verificar exclusões primeiro
    for pattern in exclude_patterns:
        if pattern in src_lower:
            return False
    
    # Verificar se é uma imagem muito pequena (provavelmente ícone)
    if any(size in src_lower for size in ['16x16', '24x24', '32x32', '48x48', '64x64']):
        return False
    
    # Verificar padrões da loja específica
    patterns = store_patterns.get(store_name, [])
    for pattern in patterns:
        if pattern in src_lower:
            return True
    
    # Verificar extensões de imagem válidas
    if not any(src_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        return False
    
    # Verificar se parece uma URL de produto (não muito genérica)
    if 'http' in src_lower:
        product_indicators = ['product', 'prod', 'item', 'image', 'photo', 'pic', 'gallery']
        if not any(indicator in src_lower for indicator in product_indicators):
            return False
    
    return True

def extract_images_with_selenium(url, store_name):
    """Extrai imagens usando Selenium com filtros rigorosos"""
    driver = None
    try:
        print(f"Acessando {store_name} com Selenium headless...")
        
        driver = setup_chrome_driver_with_retry()
        if not driver:
            print("❌ Falha ao configurar o driver do Chrome")
            return []
        
        print("Navegando para a URL...")
        driver.get(url)
        
        if not wait_for_page_load(driver):
            print("⚠️ Página não carregou completamente, mas continuando...")
        
        print("Aguardando carregamento de imagens...")
        if not wait_for_images_to_load(driver):
            print("⚠️ Imagens não carregaram completamente, mas continuando...")
        
        images_found = []
        
        # Estratégia 1: Imagens normais
        print("Buscando imagens <img>...")
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        print(f"Encontradas {len(img_elements)} imagens <img>")
        
        for img in img_elements:
            try:
                src = img.get_attribute('src')
                if src and is_main_product_image(src, img, store_name):
                    image_info = create_image_info(src, img, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 2: Imagens com lazy loading
        print("Buscando imagens com lazy loading...")
        lazy_images = driver.find_elements(By.CSS_SELECTOR, "img[data-src], img[data-lazy-src], img[data-original]")
        print(f"Encontradas {len(lazy_images)} imagens lazy loading")
        
        for img in lazy_images:
            try:
                src = img.get_attribute('data-src') or img.get_attribute('data-lazy-src') or img.get_attribute('data-original')
                if src and is_main_product_image(src, img, store_name):
                    image_info = create_image_info(src, img, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 3: Meta tags de imagem
        print("Buscando meta tags de imagem...")
        meta_images = driver.find_elements(By.CSS_SELECTOR, "meta[property*='image']")
        print(f"Encontradas {len(meta_images)} meta tags de imagem")
        
        for meta in meta_images:
            try:
                content = meta.get_attribute('content')
                if content and is_main_product_image(content, meta, store_name):
                    image_info = create_image_info(content, meta, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        print(f"✅ Total de imagens encontradas: {len(images_found)}")
        return images_found
        
    except Exception as e:
        print(f"❌ Erro durante a extração: {str(e)}")
        print(f"Stack trace: {e.__class__.__name__}")
        return []
    
    finally:
        if driver:
            try:
                print("🔄 Fechando driver do Chrome...")
                driver.quit()
                print("✅ Driver fechado com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao fechar driver: {e}")
                pass

def create_image_info(src, element, store_name):
    """Cria informações da imagem com dados para ordenação por qualidade"""
    try:
        file_size = get_image_dimensions(src)
        
        return {
            'url': src,
            'alt': element.get_attribute('alt') or '',
            'title': element.get_attribute('title') or '',
            'width': element.get_attribute('width') or '',
            'height': element.get_attribute('height') or '',
            'class': element.get_attribute('class') or '',
            'id': element.get_attribute('id') or '',
            'element_type': element.tag_name,
            'file_size_bytes': file_size,
            'quality_score': 0
        }
    except:
        return {
            'url': src,
            'alt': '',
            'title': '',
            'width': '',
            'height': '',
            'class': '',
            'id': '',
            'element_type': 'unknown',
            'file_size_bytes': 0,
            'quality_score': 0
        }

def calculate_quality_score(image_info, store_name):
    """Calcula score de qualidade baseado em resolução e tamanho real"""
    score = 0
    url = image_info['url'].lower()
    
    # Pontuar por tamanho do arquivo (mais preciso que dimensões HTML)
    if image_info['file_size_bytes'] > 0:
        # Normalizar tamanho: 1MB = 100 pontos
        score += (image_info['file_size_bytes'] / 1024 / 1024) * 100
    
    # Pontuar por dimensões HTML (se disponível)
    if image_info['width'] and image_info['height']:
        try:
            width = int(image_info['width'])
            height = int(image_info['height'])
            # Normalizar: 1000x1000 = 50 pontos
            score += (width * height) / 20000
        except:
            pass
    
    # Pontuar por extensão de arquivo
    if url.endswith('.jpg') or url.endswith('.jpeg'):
        score += 15
    elif url.endswith('.png'):
        score += 12
    elif url.endswith('.webp'):
        score += 10
    
    # Pontuar por padrões específicos da loja
    if store_name == 'Amazon':
        if 'images-na.ssl-images-amazon.com/images/' in url:
            score += 30
        if 'm.media-amazon.com/images/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    elif store_name == 'Mercado Livre':
        if 'http2.mlstatic.com/D_' in url:
            score += 30
        if 'mlstatic.com/' in url:
            score += 25
        if 'product' in url:
            score += 20
    
    elif store_name == 'AliExpress':
        if 'ae01.alicdn.com/kf/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    elif store_name == 'Americanas':
        if 'americanas.vtexassets.com/arquivos/ids/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    elif store_name == 'Casas Bahia':
        if 'casasbahia.com.br/arquivos/ids/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    elif store_name == 'Shopee':
        if 'shopee.com.br/arquivos/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    elif store_name == 'Shein':
        if 'img.ltwebstatic.com/images3_ccc/' in url:
            score += 30
        if 'product' in url:
            score += 25
    
    # Pontuar por padrões de qualidade na URL
    if any(term in url for term in ['high', 'large', 'original', 'full', 'hd', '4k', '1280', '1920']):
        score += 25
    
    # Pontuar por alt text significativo
    if len(image_info['alt']) > 20:
        score += 15
    
    return score

def get_base_image_url(url):
    """Remove parâmetros de URL para identificar imagens duplicadas"""
    base_url = url.split('?')[0].split('#')[0]
    
    # Remover parâmetros de tamanho específicos
    base_url = re.sub(r'\._AC_[^_]+_\.', '._AC_.', base_url)
    base_url = re.sub(r'\._SS\d+_\.', '._SS_.', base_url)
    base_url = re.sub(r'\._SY\d+_\.', '._SY_.', base_url)
    
    return base_url

def extract_product_images(url, store_name=None):
    """
    Função principal para extrair imagens de produto
    
    Args:
        url (str): URL do produto
        store_name (str, optional): Nome da loja (será detectado automaticamente se não fornecido)
    
    Returns:
        dict: Dicionário com informações das imagens extraídas
    """
    try:
        # Detectar loja automaticamente se não fornecida
        if not store_name:
            store_name = detect_store_from_url(url)
        
        print(f"Iniciando extração para {store_name}: {url}")
        
        # Extrair imagens
        images = extract_images_with_selenium(url, store_name)
        
        if not images:
            return None
        
        print(f"Encontradas {len(images)} imagens de produto")
        
        # Calcular scores de qualidade
        for img in images:
            img['quality_score'] = calculate_quality_score(img, store_name)
        
        # Ordenar por qualidade (melhor para pior)
        images.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Remover duplicatas baseado na URL base
        unique_images = []
        seen_urls = set()
        
        for img in images:
            base_url = get_base_image_url(img['url'])
            if base_url not in seen_urls:
                seen_urls.add(base_url)
                unique_images.append(img)
        
        print(f"Após remoção de duplicatas: {len(unique_images)} imagens únicas")
        
        return {
            'store_name': store_name,
            'url': url,
            'extraction_date': datetime.now().isoformat(),
            'total_images_found': len(unique_images),
            'extraction_method': 'selenium_headless_product_only',
            'images': unique_images
        }
        
    except Exception as e:
        print(f"Erro na extração: {str(e)}")
        raise e
