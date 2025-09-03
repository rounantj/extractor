#!/usr/bin/env python3
"""
Teste forçado do fallback SEO - simula falha dos métodos tradicionais
"""

from image_extractor import extract_product_images
from seo_extractor import extract_seo_meta_tags

def test_forced_fallback():
    """Testa o fallback SEO forçando falha dos métodos tradicionais"""
    
    print("🚀 TESTE FORÇADO DO FALLBACK SEO")
    print("=" * 60)
    
    # URL da Shopee
    test_url = "https://shopee.com.br/Xbox-One-Fat-500gb-Controle-Fonte-i.397437271.23798539669?sp_atk=65ccce74-36a3-4ff7-b9be-d674e0640fc5&xptdk=65ccce74-36a3-4ff7-b9be-d674e0640fc5"
    
    print(f"🔗 URL: {test_url}")
    print("-" * 60)
    
    # 1. Testar método SEO diretamente
    print("1️⃣ TESTE DIRETO DO MÉTODO SEO:")
    seo_result = extract_seo_meta_tags(test_url)
    
    if seo_result['status'] == 'success':
        print(f"✅ SEO funcionou!")
        print(f"📄 Título: {seo_result['title']}")
        print(f"📝 Descrição: {seo_result['description'][:100]}...")
        print(f"🖼️ Imagem: {seo_result['image'][:80] if seo_result['image'] else 'N/A'}...")
        print(f"🔍 Fonte: {seo_result['source']}")
    else:
        print(f"❌ SEO falhou: {seo_result.get('error', 'Erro desconhecido')}")
    
    print("\n" + "-" * 60)
    
    # 2. Simular fallback manualmente
    print("2️⃣ SIMULAÇÃO DO FALLBACK:")
    
    # Simular que os métodos tradicionais falharam
    images = []  # Lista vazia = falha dos métodos tradicionais
    
    if not images:
        print("🔄 Métodos tradicionais falharam, tentando fallback SEO estilo WhatsApp...")
        seo_result = extract_seo_meta_tags(test_url)
        
        if seo_result['status'] == 'success' and seo_result.get('image'):
            # Criar uma imagem fake baseada no resultado SEO
            seo_image = {
                'url': seo_result['image'],
                'alt': seo_result.get('title', ''),
                'title': seo_result.get('title', ''),
                'width': '',
                'height': '',
                'class': '',
                'id': '',
                'element_type': 'seo_fallback',
                'file_size_bytes': 0,
                'quality_score': 50  # Score médio para SEO
            }
            images = [seo_image]
            print(f"✅ Fallback SEO encontrou 1 imagem: {seo_result['image'][:80]}...")
            
            print(f"\n📊 RESULTADO DO FALLBACK:")
            print(f"🖼️ Imagem: {seo_image['url'][:80]}...")
            print(f"📄 Título: {seo_image['title'][:50]}...")
            print(f"🔧 Tipo: {seo_image['element_type']}")
            print(f"⭐ Score: {seo_image['quality_score']}")
        else:
            print("❌ Fallback SEO também falhou")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_forced_fallback()
