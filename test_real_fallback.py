#!/usr/bin/env python3
"""
Teste real do fallback com sites que realmente falham
"""

from image_extractor import extract_product_images

def test_real_fallback():
    """Testa o fallback SEO com sites que realmente falham nos métodos tradicionais"""
    
    # URLs que provavelmente vão falhar nos métodos tradicionais
    test_urls = [
        {
            "url": "https://www.shein.com.br/product-page/123456",
            "name": "Shein (site chinês - deve usar fallback)"
        },
        {
            "url": "https://www.taobao.com/item/123456.htm",
            "name": "Taobao (site chinês - deve usar fallback)"
        },
        {
            "url": "https://www.1688.com/offer/123456.html",
            "name": "1688 (site chinês - deve usar fallback)"
        }
    ]
    
    print("🚀 TESTE REAL DO FALLBACK SEO")
    print("=" * 60)
    
    for i, test in enumerate(test_urls, 1):
        print(f"\n🔗 TESTE {i}: {test['name']}")
        print(f"URL: {test['url']}")
        print("-" * 60)
        
        try:
            result = extract_product_images(test['url'])
            
            if result:
                print(f"✅ SUCESSO!")
                print(f"🏪 Loja: {result['store_name']}")
                print(f"📊 Total de imagens: {result['total_images_found']}")
                print(f"🔧 Método usado: {result['extraction_method']}")
                
                if result['images']:
                    print(f"🖼️ Primeira imagem:")
                    first_img = result['images'][0]
                    print(f"  • URL: {first_img['url'][:80]}...")
                    print(f"  • Título: {first_img.get('title', 'N/A')[:50]}...")
                    print(f"  • Tipo: {first_img.get('element_type', 'N/A')}")
                    print(f"  • Score: {first_img.get('quality_score', 0)}")
                
                # Verificar se usou fallback SEO
                if result['extraction_method'] == 'seo_whatsapp_fallback':
                    print("🎯 FALLBACK SEO ATIVADO!")
                else:
                    print("⚡ Método tradicional funcionou")
                    
            else:
                print("❌ FALHA: Nenhuma imagem encontrada")
                
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_real_fallback()
