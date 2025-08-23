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
from bs4 import BeautifulSoup
import tempfile
import shutil

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
    elif 'kabum' in url_lower:
        return 'Kabum'
    else:
        return 'Generic'

def setup_chrome_driver_heroku():
    """Configuração do Chrome baseada em soluções comprovadas do Heroku"""
    try:
        chrome_options = Options()
        
        # SOLUÇÃO COMPROVADA: Configurações mínimas que funcionam no Heroku
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # SOLUÇÃO COMPROVADA: Usar diretório temporário único e limpo
        temp_dir = f"/tmp/chrome-{os.getpid()}-{int(time.time())}"
        os.makedirs(temp_dir, exist_ok=True)
        
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        chrome_options.add_argument(f'--data-path={temp_dir}')
        chrome_options.add_argument(f'--homedir={temp_dir}')
        chrome_options.add_argument(f'--disk-cache-dir={temp_dir}/cache')
        
        # SOLUÇÃO COMPROVADA: Configurações de isolamento
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--no-zygote')
        chrome_options.add_argument('--disable-setuid-sandbox')
        
        # SOLUÇÃO COMPROVADA: Configurações de memória
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        
        # SOLUÇÃO COMPROVADA: Configurações de rede
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--no-report-upload')
        
        # SOLUÇÃO COMPROVADA: Configurações de janela
        chrome_options.add_argument('--window-size=1366,768')
        chrome_options.add_argument('--start-maximized')
        
        # SOLUÇÃO COMPROVADA: User agent realista
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # SOLUÇÃO COMPROVADA: Configurações experimentais
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # SOLUÇÃO COMPROVADA: Configurações de segurança
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        print(f"🔧 Configurando Chrome com diretório temporário: {temp_dir}")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome configurado com sucesso para Heroku")
        return driver, temp_dir
        
    except Exception as e:
        print(f"❌ Erro ao configurar Chrome para Heroku: {e}")
        return None, None

def cleanup_chrome_temp_dir(temp_dir):
    """Limpa o diretório temporário do Chrome"""
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"🧹 Diretório temporário limpo: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Erro ao limpar diretório: {e}")

def extract_images_with_requests(url, store_name):
    """Fallback: Extrai imagens usando requests + BeautifulSoup"""
    try:
        print(f"🔄 Fallback: Extraindo com requests + BeautifulSoup para {store_name}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images_found = []
        
        # Buscar imagens <img>
        img_elements = soup.find_all('img')
        print(f"📸 Encontradas {len(img_elements)} imagens <img> via requests")
        
        for img in img_elements:
            try:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if src and is_main_product_image(src, img, store_name):
                    # Converter para URL absoluta se necessário
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(url, src)
                    elif not src.startswith('http'):
                        src = urljoin(url, src)
                    
                    image_info = create_image_info(src, img, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Buscar meta tags de imagem
        meta_images = soup.find_all('meta', property=re.compile(r'image', re.I))
        print(f"📸 Encontradas {len(meta_images)} meta tags de imagem via requests")
        
        for meta in meta_images:
            try:
                content = meta.get('content')
                if content and is_main_product_image(content, meta, store_name):
                    if content.startswith('//'):
                        content = 'https:' + content
                    elif content.startswith('/'):
                        content = urljoin(url, content)
                    elif not content.startswith('http'):
                        content = urljoin(url, content)
                    
                    image_info = create_image_info(content, meta, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        print(f"✅ Total de imagens encontradas via requests: {len(images_found)}")
        return images_found
        
    except Exception as e:
        print(f"❌ Erro no fallback com requests: {str(e)}")
        return []

def extract_images_with_selenium(url, store_name):
    """Extrai imagens usando Selenium - versão otimizada para Heroku"""
    driver = None
    temp_dir = None
    try:
        print(f"🚀 Tentando extração com Selenium para {store_name}...")
        
        driver, temp_dir = setup_chrome_driver_heroku()
        if not driver:
            print("❌ Falha ao configurar Chrome, tentando fallback...")
            return None
        
        print("🌐 Navegando para a URL...")
        driver.get(url)
        
        # Aguardar carregamento básico
        time.sleep(random.uniform(3, 5))
        
        images_found = []
        
        # Buscar imagens <img>
        print("🔍 Buscando imagens <img>...")
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        print(f"📸 Encontradas {len(img_elements)} imagens <img>")
        
        for img in img_elements:
            try:
                src = img.get_attribute('src')
                if src and is_main_product_image(src, img, store_name):
                    image_info = create_image_info(src, img, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Buscar imagens com lazy loading
        print("🔍 Buscando imagens com lazy loading...")
        lazy_images = driver.find_elements(By.CSS_SELECTOR, "img[data-src], img[data-lazy-src], img[data-original]")
        print(f"📸 Encontradas {len(lazy_images)} imagens lazy loading")
        
        for img in lazy_images:
            try:
                src = img.get_attribute('data-src') or img.get_attribute('data-lazy-src') or img.get_attribute('data-original')
                if src and is_main_product_image(src, img, store_name):
                    image_info = create_image_info(src, img, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Buscar meta tags
        print("🔍 Buscando meta tags de imagem...")
        meta_images = driver.find_elements(By.CSS_SELECTOR, "meta[property*='image']")
        print(f"📸 Encontradas {len(meta_images)} meta tags de imagem")
        
        for meta in meta_images:
            try:
                content = meta.get_attribute('content')
                if content and is_main_product_image(content, meta, store_name):
                    image_info = create_image_info(content, meta, store_name)
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        print(f"✅ Selenium encontrou {len(images_found)} imagens")
        return images_found
        
    except Exception as e:
        print(f"❌ Erro no Selenium: {str(e)}")
        return None
    
    finally:
        if driver:
            try:
                print("🧹 Limpando recursos do Chrome...")
                driver.quit()
                print("✅ Chrome fechado com sucesso")
            except Exception as e:
                print(f"⚠️ Erro ao fechar Chrome: {e}")
        
        # Limpar diretório temporário
        if temp_dir:
            cleanup_chrome_temp_dir(temp_dir)

def is_main_product_image(src, element, store_name):
    """Filtro rigoroso para imagens principais de produto"""
    if not src:
        return False
    
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
        ],
        'Kabum': [
            'images.kabum.com.br/produtos/fotos/',
            'kabum.com.br/produtos/fotos/',
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

def create_image_info(src, element, store_name):
    """Cria informações da imagem com dados para ordenação por qualidade"""
    try:
        file_size = get_image_dimensions(src)
        
        # Extrair atributos baseado no tipo de elemento
        if hasattr(element, 'get'):
            # Elemento BeautifulSoup
            alt = element.get('alt', '')
            title = element.get('title', '')
            width = element.get('width', '')
            height = element.get('height', '')
            class_attr = element.get('class', '')
            id_attr = element.get('id', '')
            tag_name = element.name
        else:
            # Elemento Selenium
            alt = element.get_attribute('alt') or ''
            title = element.get_attribute('title') or ''
            width = element.get_attribute('width') or ''
            height = element.get_attribute('height') or ''
            class_attr = element.get_attribute('class') or ''
            id_attr = element.get_attribute('id') or ''
            tag_name = element.tag_name
        
        return {
            'url': src,
            'alt': alt,
            'title': title,
            'width': width,
            'height': height,
            'class': class_attr,
            'id': id_attr,
            'element_type': tag_name,
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
    
    elif store_name == 'Kabum':
        if 'images.kabum.com.br/produtos/fotos/' in url:
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
    Função principal para extrair imagens de produto com estratégia híbrida
    
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
        
        # Estratégia 1: Tentar Selenium primeiro (mais robusto)
        images = extract_images_with_selenium(url, store_name)
        
        # Estratégia 2: Se Selenium falhar, usar requests + BeautifulSoup
        if not images:
            print("🔄 Selenium falhou, tentando fallback com requests...")
            images = extract_images_with_requests(url, store_name)
        
        if not images:
            print("❌ Nenhuma imagem encontrada com nenhuma estratégia")
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
        
        # Determinar método de extração usado
        extraction_method = 'selenium_headless' if images else 'requests_beautifulsoup'
        
        return {
            'store_name': store_name,
            'url': url,
            'extraction_date': datetime.now().isoformat(),
            'total_images_found': len(unique_images),
            'extraction_method': extraction_method,
            'images': unique_images
        }
        
    except Exception as e:
        print(f"Erro na extração: {str(e)}")
        raise e
