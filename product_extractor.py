"""
Extrator de Produtos Completo
Usa Selenium para scraping robusto de e-commerce

Suporta:
- Mercado Livre (com proxy)
- Amazon
- Shopee
- AliExpress
- Shein
- Magazine Luiza
- Kabum
- Sites genéricos
"""

import os
import re
import time
import random
import json
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Import helpers do image_extractor
from image_extractor import (
    setup_chrome_driver_heroku,
    cleanup_chrome_temp_dir,
    get_proxies_for_url,
    normalize_mercado_livre_url,
)


@dataclass
class ExtractedProduct:
    """Estrutura de dados do produto extraído"""
    url: str
    platform: str
    title: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "BRL"
    description: Optional[str] = None
    images: List[str] = None
    seller: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    specifications: Dict[str, str] = None
    raw_html: Optional[str] = None
    extraction_method: str = "selenium"
    status: str = "success"
    error: Optional[str] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.specifications is None:
            self.specifications = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def detect_platform(url: str) -> str:
    """Detecta a plataforma de e-commerce pela URL"""
    url_lower = url.lower()
    
    if 'mercadolivre' in url_lower or 'mercadolibre' in url_lower or 'mlstatic.com' in url_lower:
        return 'mercadolivre'
    elif 'amazon' in url_lower or 'amzn' in url_lower:
        return 'amazon'
    elif 'shopee' in url_lower:
        return 'shopee'
    elif 'aliexpress' in url_lower:
        return 'aliexpress'
    elif 'shein' in url_lower:
        return 'shein'
    elif 'magalu' in url_lower or 'magazineluiza' in url_lower:
        return 'magazineluiza'
    elif 'kabum' in url_lower:
        return 'kabum'
    elif 'americanas' in url_lower:
        return 'americanas'
    else:
        return 'generic'


def resolve_shortened_url(url: str) -> str:
    """Resolve URLs encurtadas (amzn.to, bit.ly, etc)"""
    shorteners = ['amzn.to', 'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'cutt.ly']
    
    try:
        parsed = urlparse(url)
        if any(s in parsed.netloc.lower() for s in shorteners):
            print(f"↪️ Resolvendo URL encurtada: {url}")
            response = requests.head(url, allow_redirects=True, timeout=10)
            resolved = response.url
            print(f"   ➡️ Resolvido para: {resolved}")
            return resolved
    except Exception as e:
        print(f"⚠️ Erro ao resolver URL: {e}")
    
    return url


def parse_price(price_str: str) -> Optional[float]:
    """Converte string de preço para float"""
    if not price_str:
        return None
    
    try:
        # Remover símbolos de moeda e espaços
        cleaned = re.sub(r'[R$€£¥\s]', '', price_str)
        # Converter formato brasileiro (1.234,56) para float
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        return float(cleaned)
    except (ValueError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════════════════════
# EXTRATORES POR PLATAFORMA
# ═══════════════════════════════════════════════════════════════════════════

def extract_mercadolivre_with_api(url: str) -> Optional[ExtractedProduct]:
    """Extrai produto do Mercado Livre via API pública"""
    print("🟡 [ML]: Tentando via API pública...")
    
    try:
        # Extrair ID do item
        item_id = None
        parsed = urlparse(url)
        
        # Padrão: /p/MLBxxxx ou MLBxxxx no path
        match = re.search(r'(ML[A-Z]{1,2}\d+)', url.upper())
        if match:
            item_id = match.group(1)
        
        if not item_id:
            print("   ❌ Não foi possível extrair ID do item")
            return None
        
        print(f"   📌 Item ID: {item_id}")
        
        # Buscar na API
        api_url = f"https://api.mercadolibre.com/items/{item_id}"
        proxies = get_proxies_for_url(url, 'Mercado Livre')
        
        response = requests.get(api_url, proxies=proxies, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Buscar descrição
        description = ""
        try:
            desc_response = requests.get(f"{api_url}/description", proxies=proxies, timeout=10)
            if desc_response.ok:
                desc_data = desc_response.json()
                description = desc_data.get('plain_text', '') or desc_data.get('text', '')
        except:
            pass
        
        # Extrair imagens
        images = []
        if data.get('pictures'):
            images = [p.get('url') or p.get('secure_url') for p in data['pictures'] if p.get('url') or p.get('secure_url')]
        elif data.get('thumbnail'):
            images = [data['thumbnail']]
        
        # Buscar nome do vendedor
        seller = "Mercado Livre"
        try:
            if data.get('seller_id'):
                seller_response = requests.get(
                    f"https://api.mercadolibre.com/users/{data['seller_id']}",
                    proxies=proxies,
                    timeout=10
                )
                if seller_response.ok:
                    seller = seller_response.json().get('nickname', 'Mercado Livre')
        except:
            pass
        
        product = ExtractedProduct(
            url=url,
            platform='mercadolivre',
            title=data.get('title'),
            price=data.get('price'),
            original_price=data.get('original_price'),
            currency=data.get('currency_id', 'BRL'),
            description=description[:1000] if description else None,
            images=images[:10],
            seller=seller,
            extraction_method='mercadolivre_api'
        )
        
        print(f"   ✅ Extraído via API: {product.title[:50]}...")
        return product
        
    except Exception as e:
        print(f"   ❌ API falhou: {e}")
        return None


def extract_mercadolivre_with_html(url: str) -> Optional[ExtractedProduct]:
    """Extrai produto do Mercado Livre via HTML scraping"""
    print("🟡 [ML]: Tentando via HTML scraping...")
    
    # Normalizar URL
    url = normalize_mercado_livre_url(url)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://www.mercadolivre.com.br/',
        }
        
        proxies = get_proxies_for_url(url, 'Mercado Livre')
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Título
        title = None
        title_el = soup.select_one('h1.ui-pdp-title')
        if title_el:
            title = title_el.get_text(strip=True)
        
        # Preço
        price = None
        price_el = soup.select_one('.ui-pdp-price__second-line .andes-money-amount__fraction')
        if price_el:
            price = parse_price(price_el.get_text(strip=True))
        
        # Preço original
        original_price = None
        original_el = soup.select_one('.ui-pdp-price__second-line .andes-money-amount--previous .andes-money-amount__fraction')
        if original_el:
            original_price = parse_price(original_el.get_text(strip=True))
        
        # Descrição
        description = None
        desc_el = soup.select_one('.ui-pdp-description__content')
        if desc_el:
            description = desc_el.get_text(strip=True)[:1000]
        
        # Imagens
        images = []
        for img in soup.select('.ui-pdp-gallery__figure img'):
            src = img.get('src') or img.get('data-src')
            if src and 'mlstatic.com' in src:
                images.append(src)
        
        # Vendedor
        seller = None
        seller_el = soup.select_one('.ui-pdp-seller__link-trigger')
        if seller_el:
            seller = seller_el.get_text(strip=True)
        
        if not title and not price:
            return None
        
        product = ExtractedProduct(
            url=url,
            platform='mercadolivre',
            title=title,
            price=price,
            original_price=original_price,
            description=description,
            images=images[:10],
            seller=seller,
            extraction_method='html_scraping'
        )
        
        print(f"   ✅ Extraído via HTML: {product.title[:50] if product.title else 'N/A'}...")
        return product
        
    except Exception as e:
        print(f"   ❌ HTML scraping falhou: {e}")
        return None


def extract_amazon(url: str) -> Optional[ExtractedProduct]:
    """Extrai produto da Amazon"""
    print("🟠 [Amazon]: Extraindo...")
    
    driver = None
    temp_dir = None
    
    try:
        driver, temp_dir = setup_chrome_driver_heroku()
        if not driver:
            return None
        
        driver.get(url)
        time.sleep(random.uniform(2, 4))
        
        # Título
        title = None
        try:
            title_el = driver.find_element(By.ID, 'productTitle')
            title = title_el.text.strip()
        except:
            pass
        
        # Preço
        price = None
        try:
            price_el = driver.find_element(By.CSS_SELECTOR, '.a-price-whole')
            price = parse_price(price_el.text)
        except:
            pass
        
        # Descrição
        description = None
        try:
            desc_el = driver.find_element(By.ID, 'productDescription')
            description = desc_el.text.strip()[:1000]
        except:
            pass
        
        # Imagens
        images = []
        try:
            for img in driver.find_elements(By.CSS_SELECTOR, '#altImages img, #imgTagWrapperId img'):
                src = img.get_attribute('src')
                if src and 'amazon.com' in src and 'icon' not in src.lower():
                    # Converter para alta resolução
                    src = re.sub(r'\._[^.]+_\.', '.', src)
                    images.append(src)
        except:
            pass
        
        product = ExtractedProduct(
            url=url,
            platform='amazon',
            title=title,
            price=price,
            description=description,
            images=list(set(images))[:10],
            extraction_method='selenium'
        )
        
        print(f"   ✅ Extraído: {product.title[:50] if product.title else 'N/A'}...")
        return product
        
    except Exception as e:
        print(f"   ❌ Extração falhou: {e}")
        return None
    finally:
        if driver:
            driver.quit()
        if temp_dir:
            cleanup_chrome_temp_dir(temp_dir)


def extract_generic(url: str) -> ExtractedProduct:
    """Extrai produto de site genérico usando meta tags"""
    print("🔵 [Generic]: Extraindo via meta tags...")
    
    try:
        headers = {
            'User-Agent': 'WhatsApp/2.23.24.81 (iPhone; iOS 17.1.2; Scale/3.00)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Open Graph tags
        title = None
        description = None
        image = None
        price = None
        
        for meta in soup.find_all('meta'):
            prop = meta.get('property', '') or meta.get('name', '')
            content = meta.get('content', '')
            
            if 'og:title' in prop:
                title = content
            elif 'og:description' in prop:
                description = content
            elif 'og:image' in prop:
                image = content
            elif 'product:price:amount' in prop:
                price = parse_price(content)
        
        # Fallbacks
        if not title:
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else None
        
        if not description:
            desc_meta = soup.find('meta', attrs={'name': 'description'})
            description = desc_meta.get('content', '') if desc_meta else None
        
        images = [image] if image else []
        
        product = ExtractedProduct(
            url=url,
            platform='generic',
            title=title,
            price=price,
            description=description[:1000] if description else None,
            images=images,
            extraction_method='meta_tags'
        )
        
        print(f"   ✅ Extraído: {product.title[:50] if product.title else 'N/A'}...")
        return product
        
    except Exception as e:
        print(f"   ❌ Extração genérica falhou: {e}")
        return ExtractedProduct(
            url=url,
            platform='generic',
            status='error',
            error=str(e)
        )


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def extract_product(url: str) -> ExtractedProduct:
    """
    Função principal de extração de produtos
    
    Args:
        url: URL do produto
    
    Returns:
        ExtractedProduct com dados do produto
    """
    print(f"\n{'='*80}")
    print(f"📦 Iniciando extração de produto...")
    print(f"   URL: {url}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    # Resolver URLs encurtadas
    resolved_url = resolve_shortened_url(url)
    
    # Detectar plataforma
    platform = detect_platform(resolved_url)
    print(f"🏪 Plataforma detectada: {platform}")
    
    product = None
    
    # Roteamento por plataforma
    if platform == 'mercadolivre':
        # Tentar API primeiro, depois HTML
        product = extract_mercadolivre_with_api(resolved_url)
        if not product or not product.title:
            product = extract_mercadolivre_with_html(resolved_url)
    
    elif platform == 'amazon':
        product = extract_amazon(resolved_url)
    
    # Fallback para extração genérica
    if not product or not product.title:
        print("⚠️ Usando extração genérica como fallback...")
        product = extract_generic(resolved_url)
    
    # Garantir que URL original está no resultado
    product.url = url
    
    duration = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"✅ Extração concluída em {duration:.2f}s")
    print(f"   Título: {product.title[:60] if product.title else 'N/A'}...")
    print(f"   Preço: R$ {product.price or 'N/A'}")
    print(f"   Imagens: {len(product.images)}")
    print(f"   Método: {product.extraction_method}")
    print(f"{'='*80}\n")
    
    return product


if __name__ == "__main__":
    # Teste local
    test_urls = [
        "https://www.mercadolivre.com.br/p/MLB123456789",
        "https://www.amazon.com.br/dp/B09EXAMPLE",
    ]
    
    for url in test_urls:
        result = extract_product(url)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

