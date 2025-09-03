#!/usr/bin/env python3
"""
Script para testar o endpoint SEO da API
"""

import requests
import json
import time

def test_seo_endpoint():
    """Testa o endpoint /extract-seo"""
    
    # URL da API (ajuste conforme necessário)
    api_url = "http://localhost:4000/extract-seo"
    
    # URL de teste (Shopee)
    test_url = "https://shopee.com.br/Xbox-One-Fat-500gb-Controle-Fonte-i.397437271.23798539669?sp_atk=65ccce74-36a3-4ff7-b9be-d674e0640fc5&xptdk=65ccce74-36a3-4ff7-b9be-d674e0640fc5"
    
    print("🚀 TESTE DO ENDPOINT SEO")
    print("=" * 50)
    print(f"🔗 API URL: {api_url}")
    print(f"🔗 Test URL: {test_url}")
    print("=" * 50)
    
    # Dados da requisição
    data = {
        "url": test_url
    }
    
    try:
        print("📡 Enviando requisição...")
        response = requests.post(api_url, json=data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO!")
            print(f"📄 Título: {result['title']}")
            print(f"📝 Descrição: {result['description'][:100]}...")
            print(f"🖼️ Imagem: {result['image'][:80] if result['image'] else 'N/A'}...")
            print(f"🔍 Fonte: {result['source']}")
            print(f"📊 Status: {result['status']}")
        else:
            print("❌ ERRO!")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API")
        print("💡 Certifique-se de que a API está rodando:")
        print("   python3 main.py")
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

def test_direct_method():
    """Testa o método diretamente (sem API)"""
    
    print("\n🔧 TESTE DIRETO (SEM API)")
    print("=" * 50)
    
    try:
        from seo_extractor import extract_seo_meta_tags
        
        test_url = "https://shopee.com.br/Xbox-One-Fat-500gb-Controle-Fonte-i.397437271.23798539669?sp_atk=65ccce74-36a3-4ff7-b9be-d674e0640fc5&xptdk=65ccce74-36a3-4ff7-b9be-d674e0640fc5"
        
        result = extract_seo_meta_tags(test_url)
        
        if result['status'] == 'success':
            print("✅ SUCESSO!")
            print(f"📄 Título: {result['title']}")
            print(f"📝 Descrição: {result['description'][:100]}...")
            print(f"🖼️ Imagem: {result['image'][:80] if result['image'] else 'N/A'}...")
            print(f"🔍 Fonte: {result['source']}")
        else:
            print("❌ ERRO!")
            print(f"Erro: {result.get('error', 'Desconhecido')}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

if __name__ == "__main__":
    # Teste direto primeiro
    test_direct_method()
    
    # Teste da API
    test_seo_endpoint()
