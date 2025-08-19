#!/usr/bin/env python3
"""
Script de teste para a API de extração de imagens
"""

import requests
import json
import time

def test_api():
    """Testa a API localmente"""
    
    # URL da API local
    base_url = "http://localhost:4000"
    
    # URLs de teste
    test_urls = [
        {
            "name": "Amazon - Lanterna",
            "url": "https://www.amazon.com.br/Lanterna-Recarreg%C3%A1vel-lanternas-Acampamento-Emerg%C3%AAncias/dp/B0DKWV28CZ/ref=cml-home?pf_rd_p=3d1066c6-ffd4-4028-95fb-4cbb82efae0f&pf_rd_r=0YDBDSYWXQ0BJ038N9A5&sr=1-4-a1b8652d-a8b0-47e5-88a4-2995681a52d7&ufe=app_do%3Aamzn1.fos.6121c6c4-c969-43ae-92f7-cc248fc6181d&th=1"
        },
        {
            "name": "Mercado Livre - Afiador",
            "url": "https://www.mercadolivre.com.br/afiador-amolador-de-facas-3-opcoes-de-afiar-profissional-moderna-mix/p/MLB51900969?pdp_filters=price%3A*-19%7Cdeal%3AMLB1339640-1#polycard_client=search-nordic&searchVariation=MLB51900969&wid=MLB5469833884&position=9&search_layout=grid&type=product&tracking_id=3ce4d1bf-28f6-4f25-a58f-f3229e8f97f7&sid=search"
        }
    ]
    
    print("🧪 Testando API de Extração de Imagens")
    print("=" * 60)
    
    # Testar endpoint raiz
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Endpoint raiz funcionando")
            print(f"   {response.json()}")
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar endpoint raiz: {e}")
        return
    
    # Testar health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check funcionando")
            print(f"   {response.json()}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar health check: {e}")
    
    print("\n" + "=" * 60)
    
    # Testar extração de imagens
    for test in test_urls:
        print(f"\n🔍 Testando: {test['name']}")
        print(f"   URL: {test['url'][:80]}...")
        
        try:
            # Preparar request
            payload = {
                "url": test['url']
            }
            
            print("   📤 Enviando request...")
            start_time = time.time()
            
            # Fazer request
            response = requests.post(
                f"{base_url}/extract-images",
                json=payload,
                timeout=120  # 2 minutos de timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Sucesso! ({duration:.1f}s)")
                print(f"   🏪 Loja detectada: {result['store_name']}")
                print(f"   📸 Total encontrado: {result['total_images_found']}")
                print(f"   🏆 Top 15 retornadas: {len(result['top_15_images'])}")
                
                # Mostrar top 3 imagens
                print(f"   🥇 Top 3 imagens:")
                for i, img in enumerate(result['top_15_images'][:3], 1):
                    print(f"      {i}. Score: {img['quality_score']:6.1f} | {img['url'][:60]}...")
                
            else:
                print(f"   ❌ Falhou: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"      Erro: {error_detail.get('detail', 'Desconhecido')}")
                except:
                    print(f"      Erro: {response.text[:100]}...")
                    
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - demorou mais de 2 minutos")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
        
        print("-" * 40)
    
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    test_api()
