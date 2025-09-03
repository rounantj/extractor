#!/usr/bin/env python3
"""
Script de teste para o extrator de meta tags SEO
Testa especificamente sites chineses e outros que não funcionam com métodos tradicionais
"""

import json
from image_extractor import extract_seo_meta_tags

def test_seo_extractor():
    """Testa o extrator de meta tags SEO com múltiplos sites"""
    
    # Teste com múltiplos sites
    test_urls = [
        "https://shopee.com.br/Xbox-One-Fat-500gb-Controle-Fonte-i.397437271.23798539669?sp_atk=65ccce74-36a3-4ff7-b9be-d674e0640fc5&xptdk=65ccce74-36a3-4ff7-b9be-d674e0640fc5",
        "https://www.amazon.com.br/dp/B08N5WRWNW",  # Amazon (tem meta tags)
        "https://www.mercadolivre.com.br"  # Mercado Livre (tem meta tags)
    ]
    
    print("🚀 TESTE DO EXTRATOR DE META TAGS SEO (ESTILO WHATSAPP)")
    print("=" * 70)
    
    for i, test_url in enumerate(test_urls, 1):
        print(f"\n🔗 TESTE {i}: {test_url}")
        print("-" * 70)
        
        try:
            # Extrair meta tags
            result = extract_seo_meta_tags(test_url)
            
            print(f"\n📊 RESULTADO:")
            print("-" * 30)
            
            if result['status'] == 'success':
                print(f"✅ Status: {result['status']}")
                print(f"📄 Título: {result['title']}")
                print(f"📝 Descrição: {result['description']}")
                print(f"🖼️ Imagem: {result['image']}")
                print(f"🔍 Fonte: {result['source']}")
                
                # Salvar resultado em arquivo JSON
                filename = f'test_seo_result_{i}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"💾 Resultado salvo em: {filename}")
                
            else:
                print(f"❌ Status: {result['status']}")
                print(f"🚨 Erro: {result.get('error', 'Erro desconhecido')}")
            
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
    
    print("\n" + "=" * 70)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_seo_extractor()