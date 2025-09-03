#!/usr/bin/env python3
"""
Teste do fallback SEO integrado no extrator principal
"""

from image_extractor import extract_product_images

def test_fallback():
    """Testa o fallback SEO com sites que falham nos métodos tradicionais"""
    
    # URLs de teste - algumas que falham nos métodos tradicionais
    test_urls = [
        {
            "url": "https://shopee.com.br/Xbox-One-Fat-500gb-Controle-Fonte-i.397437271.23798539669?sp_atk=65ccce74-36a3-4ff7-b9be-d674e0640fc5&xptdk=65ccce74-36a3-4ff7-b9be-d674e0640fc5",
            "name": "Shopee (deve usar fallback SEO)"
        },
        {
            "url": "https://www.amazon.com.br/dp/B08N5WRWNW",
            "name": "Amazon (método tradicional)"
        }
    ]
    
    print("🚀 TESTE DO FALLBACK SEO INTEGRADO")
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
    test_fallback()
