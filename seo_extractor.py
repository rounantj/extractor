#!/usr/bin/env python3
"""
Extrator de meta tags SEO estilo WhatsApp
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def extract_seo_meta_tags(url):
    """
    MÉTODO WHATSAPP: Simula exatamente como WhatsApp faz link preview
    - Usa headers similares aos bots de link preview
    - Extrai meta tags Open Graph, Twitter Cards e tradicionais
    - Fallback para título e primeira imagem se não houver meta tags
    
    Args:
        url (str): URL da página
    
    Returns:
        dict: Dicionário com meta tags extraídas (formato WhatsApp)
    """
    try:
        print(f"🔍 [WHATSAPP STYLE] Extraindo meta tags de: {url}")
        
        # Headers similares aos usados por bots de link preview
        headers = {
            'User-Agent': 'WhatsApp/2.23.24.81 (iPhone; iOS 17.1.2; Scale/3.00)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. PRIORIDADE: Open Graph tags (como WhatsApp prefere)
        og_title = None
        og_description = None
        og_image = None
        og_url = None
        
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            prop = meta.get('property', '').replace('og:', '')
            content = meta.get('content', '')
            if content:
                if prop == 'title':
                    og_title = content
                elif prop == 'description':
                    og_description = content
                elif prop == 'image':
                    og_image = content
                elif prop == 'url':
                    og_url = content
        
        # 2. FALLBACK: Twitter Cards se não houver Open Graph
        twitter_title = None
        twitter_description = None
        twitter_image = None
        
        if not og_title or not og_description:
            for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
                name = meta.get('name', '').replace('twitter:', '')
                content = meta.get('content', '')
                if content:
                    if name == 'title' and not og_title:
                        twitter_title = content
                    elif name == 'description' and not og_description:
                        twitter_description = content
                    elif name == 'image' and not og_image:
                        twitter_image = content
        
        # 3. FALLBACK: Meta tags tradicionais
        meta_title = None
        meta_description = None
        
        if not og_title and not twitter_title:
            title_tag = soup.find('title')
            meta_title = title_tag.get_text().strip() if title_tag else ''
        
        if not og_description and not twitter_description:
            desc_meta = soup.find('meta', attrs={'name': 'description'})
            meta_description = desc_meta.get('content', '') if desc_meta else ''
        
        # 4. FALLBACK: Primeira imagem se não houver meta image
        fallback_image = None
        if not og_image and not twitter_image:
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(url, src)
                    elif not src.startswith('http'):
                        src = urljoin(url, src)
                    fallback_image = src
                    break
        
        # 5. Construir resultado final (priorizando Open Graph)
        final_title = og_title or twitter_title or meta_title or ''
        final_description = og_description or twitter_description or meta_description or ''
        final_image = og_image or twitter_image or fallback_image
        
        # Converter URLs relativas para absolutas
        if final_image and not final_image.startswith('http'):
            if final_image.startswith('//'):
                final_image = 'https:' + final_image
            elif final_image.startswith('/'):
                final_image = urljoin(url, final_image)
            else:
                final_image = urljoin(url, final_image)
        
        result = {
            'url': url,
            'title': final_title,
            'description': final_description,
            'image': final_image,
            'source': 'og' if og_title else 'twitter' if twitter_title else 'meta',
            'status': 'success'
        }
        
        print(f"✅ [WHATSAPP STYLE] Extraído:")
        print(f"  📄 Título: {final_title[:80]}{'...' if len(final_title) > 80 else ''}")
        print(f"  📝 Descrição: {final_description[:80]}{'...' if len(final_description) > 80 else ''}")
        print(f"  🖼️ Imagem: {final_image[:80] if final_image else 'N/A'}{'...' if final_image and len(final_image) > 80 else ''}")
        print(f"  🔍 Fonte: {result['source']}")
        
        return result
        
    except Exception as e:
        print(f"❌ [WHATSAPP STYLE] Erro: {str(e)}")
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }
