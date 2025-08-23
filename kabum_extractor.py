"""
Extrator específico para o Kabum que funciona sem Chrome
Baseado na estrutura HTML específica do site
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import random

def extract_kabum_images(url):
    """Extrai imagens do Kabum usando requests + BeautifulSoup"""
    try:
        print(f"🎯 Extraindo imagens específicas do Kabum: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.kabum.com.br/',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        images_found = []
        
        # Estratégia 1: Imagens principais do produto (galeria)
        print("🔍 Buscando imagens da galeria principal...")
        gallery_images = soup.find_all('img', {'class': re.compile(r'gallery|main|principal|product', re.I)})
        print(f"📸 Encontradas {len(gallery_images)} imagens da galeria")
        
        for img in gallery_images:
            try:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if src and is_valid_kabum_image(src):
                    src = normalize_kabum_url(src, url)
                    image_info = create_kabum_image_info(src, img, 'gallery')
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 2: Imagens com padrões específicos do Kabum
        print("🔍 Buscando imagens com padrões do Kabum...")
        kabum_images = soup.find_all('img', src=re.compile(r'kabum\.com\.br|images\.kabum\.com\.br'))
        print(f"📸 Encontradas {len(kabum_images)} imagens do Kabum")
        
        for img in kabum_images:
            try:
                src = img.get('src')
                if src and is_valid_kabum_image(src):
                    src = normalize_kabum_url(src, url)
                    image_info = create_kabum_image_info(src, img, 'kabum_pattern')
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 3: Meta tags de imagem
        print("🔍 Buscando meta tags de imagem...")
        meta_images = soup.find_all('meta', property=re.compile(r'image', re.I))
        print(f"📸 Encontradas {len(meta_images)} meta tags de imagem")
        
        for meta in meta_images:
            try:
                content = meta.get('content')
                if content and is_valid_kabum_image(content):
                    content = normalize_kabum_url(content, url)
                    image_info = create_kabum_image_info(content, meta, 'meta')
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 4: Todas as imagens <img> com filtro flexível
        print("🔍 Buscando todas as imagens <img>...")
        all_images = soup.find_all('img')
        print(f"📸 Total de imagens encontradas: {len(all_images)}")
        
        for img in all_images:
            try:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if src and is_valid_kabum_image_flexible(src):
                    src = normalize_kabum_url(src, url)
                    image_info = create_kabum_image_info(src, img, 'all_images')
                    images_found.append(image_info)
            except Exception as e:
                continue
        
        # Estratégia 5: Imagens em CSS (background-image)
        print("🔍 Buscando imagens em CSS...")
        style_elements = soup.find_all('style')
        for style in style_elements:
            if style.string:
                # Extrair URLs de background-image
                background_images = re.findall(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', style.string)
                for bg_img in background_images:
                    if bg_img and is_valid_kabum_image_flexible(bg_img):
                        bg_img = normalize_kabum_url(bg_img, url)
                        image_info = create_kabum_image_info(bg_img, style, 'css')
                        images_found.append(image_info)
        
        # Estratégia 6: Imagens em atributos data-*
        print("🔍 Buscando imagens em atributos data-*...")
        data_images = soup.find_all(attrs=re.compile(r'data-.*image|data-.*img|data-.*foto'))
        for element in data_images:
            for attr_name, attr_value in element.attrs.items():
                if 'image' in attr_name.lower() or 'img' in attr_name.lower() or 'foto' in attr_name.lower():
                    if attr_value and is_valid_kabum_image_flexible(attr_value):
                        attr_value = normalize_kabum_url(attr_value, url)
                        image_info = create_kabum_image_info(attr_value, element, 'data_attr')
                        images_found.append(image_info)
        
        print(f"✅ Total de imagens encontradas no Kabum: {len(images_found)}")
        return images_found
        
    except Exception as e:
        print(f"❌ Erro ao extrair imagens do Kabum: {str(e)}")
        return []

def is_valid_kabum_image(src):
    """Verifica se é uma imagem válida do Kabum"""
    if not src:
        return False
    
    src_lower = src.lower()
    
    # Verificar se é uma URL válida
    if not src.startswith(('http://', 'https://')):
        return False
    
    # Padrões específicos do Kabum
    kabum_patterns = [
        'images.kabum.com.br/produtos/fotos/',
        'kabum.com.br/produtos/fotos/',
        'kabum.com.br',
        'produtos/fotos',
        'fotos/',
        'images/',
        'img/'
    ]
    
    # Verificar se contém padrões do Kabum
    for pattern in kabum_patterns:
        if pattern in src_lower:
            return True
    
    # Verificar extensões de imagem válidas
    if any(src_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        return True
    
    return False

def is_valid_kabum_image_flexible(src):
    """Verificação mais flexível para imagens do Kabum"""
    if not src:
        return False
    
    src_lower = src.lower()
    
    # Verificar se é uma URL válida
    if not src.startswith(('http://', 'https://')):
        return False
    
    # Padrões de EXCLUSÃO
    exclude_patterns = [
        'logo', 'icon', 'sprite', 'banner', 'ad', 'social',
        'favicon', 'avatar', 'profile', 'thumb', 'small',
        'transparent-pixel', 'grey-pixel', 'loading', 'placeholder',
        'no-image', 'blank', 'star', 'rating', 'review',
        'coupon', 'discount', 'arrow', 'chevron', 'close',
        'menu', 'hamburger', 'search', 'filter', 'sort',
        'pagination', 'vlibras', 'accessibility', 'a11y', 'libras'
    ]
    
    # Verificar exclusões
    for pattern in exclude_patterns:
        if pattern in src_lower:
            return False
    
    # Verificar se é uma imagem muito pequena
    if any(size in src_lower for size in ['16x16', '24x24', '32x32', '48x48', '64x64']):
        return False
    
    # Aceitar qualquer imagem que não seja claramente um ícone
    return True

def normalize_kabum_url(src, base_url):
    """Normaliza URLs do Kabum para URLs absolutas"""
    if src.startswith('//'):
        return 'https:' + src
    elif src.startswith('/'):
        return urljoin(base_url, src)
    elif not src.startswith('http'):
        return urljoin(base_url, src)
    return src

def create_kabum_image_info(src, element, source_type):
    """Cria informações da imagem do Kabum"""
    try:
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
            'source_type': source_type,
            'file_size_bytes': 0,
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
            'source_type': source_type,
            'file_size_bytes': 0,
            'quality_score': 0
        }

def calculate_kabum_quality_score(image_info):
    """Calcula score de qualidade para imagens do Kabum"""
    score = 0
    url = image_info['url'].lower()
    
    # Pontuar por tipo de fonte
    source_type = image_info.get('source_type', '')
    if source_type == 'gallery':
        score += 50
    elif source_type == 'kabum_pattern':
        score += 40
    elif source_type == 'meta':
        score += 35
    elif source_type == 'all_images':
        score += 20
    elif source_type == 'css':
        score += 15
    elif source_type == 'data_attr':
        score += 10
    
    # Pontuar por padrões específicos do Kabum
    if 'images.kabum.com.br/produtos/fotos/' in url:
        score += 30
    if 'kabum.com.br/produtos/fotos/' in url:
        score += 25
    if 'kabum.com.br' in url:
        score += 20
    
    # Pontuar por extensão de arquivo
    if url.endswith('.jpg') or url.endswith('.jpeg'):
        score += 15
    elif url.endswith('.png'):
        score += 12
    elif url.endswith('.webp'):
        score += 10
    
    # Pontuar por alt text significativo
    if len(image_info['alt']) > 20:
        score += 15
    
    # Pontuar por dimensões HTML
    if image_info['width'] and image_info['height']:
        try:
            width = int(image_info['width'])
            height = int(image_info['height'])
            score += (width * height) / 20000
        except:
            pass
    
    return score
