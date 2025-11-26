from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import uvicorn
import requests
from image_extractor import extract_product_images
from seo_extractor import extract_seo_meta_tags
from product_extractor import extract_product, ExtractedProduct

app = FastAPI(
    title="Extractor de Imagens de Produto",
    description="API para extrair imagens de produtos de e-commerce e meta tags SEO (estilo WhatsApp)",
    version="1.0.0"
)

class ExtractRequest(BaseModel):
    url: HttpUrl
    store_name: Optional[str] = None

class SearchImagesRequest(BaseModel):
    query: str
    count: Optional[int] = 10

class ImageInfo(BaseModel):
    url: str
    alt: str
    title: str
    width: str
    height: str
    quality_score: float
    file_size_mb: float

class ExtractResponse(BaseModel):
    store_name: str
    url: str
    total_images_found: int
    top_15_images: List[ImageInfo]
    extraction_method: str

class SearchImagesResponse(BaseModel):
    images: List[str]
    query: str
    total_found: int

class SEOExtractRequest(BaseModel):
    url: HttpUrl

class SEOExtractResponse(BaseModel):
    url: str
    title: str
    description: str
    image: Optional[str]
    source: str
    status: str


class ProductExtractRequest(BaseModel):
    url: HttpUrl


class ProductExtractResponse(BaseModel):
    url: str
    platform: str
    title: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "BRL"
    description: Optional[str] = None
    images: List[str] = []
    seller: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    specifications: Dict[str, str] = {}
    extraction_method: str = "selenium"
    status: str = "success"
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "Extractor de Imagens de Produto e Meta Tags SEO",
        "endpoints": {
            "extract_images": "/extract-images (POST)",
            "extract_seo": "/extract-seo (POST) - MÉTODO DE TESTE"
        },
        "version": "1.0.0"
    }

@app.post("/extract-images", response_model=ExtractResponse)
async def extract_images(request: ExtractRequest):
    """
    Extrai as 15 melhores imagens de produto de uma URL de e-commerce.
    
    - **url**: URL do produto (Amazon, Mercado Livre, etc.)
    - **store_name**: Nome da loja (opcional, será detectado automaticamente)
    """
    try:
        # Extrair imagens
        result = extract_product_images(str(request.url), request.store_name)
        
        if not result or not result.get('images'):
            raise HTTPException(
                status_code=404, 
                detail="Nenhuma imagem de produto encontrada"
            )
        
        # Pegar apenas as 15 primeiras (já ordenadas por qualidade)
        top_15 = result['images'][:15]
        
        # Converter para o formato de resposta
        images_response = []
        for img in top_15:
            size_mb = img.get('file_size_bytes', 0) / 1024 / 1024
            images_response.append(ImageInfo(
                url=img['url'],
                alt=img.get('alt', ''),
                title=img.get('title', ''),
                width=img.get('width', ''),
                height=img.get('height', ''),
                quality_score=img.get('quality_score', 0),
                file_size_mb=round(size_mb, 2)
            ))
        
        return ExtractResponse(
            store_name=result['store_name'],
            url=str(request.url),
            total_images_found=len(result['images']),
            top_15_images=images_response,
            extraction_method=result['extraction_method']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao extrair imagens: {str(e)}"
        )

@app.post("/extract-seo", response_model=SEOExtractResponse)
async def extract_seo_meta_tags_endpoint(request: SEOExtractRequest):
    """
    MÉTODO DE TESTE: Extrai meta tags SEO como WhatsApp faz
    Focado em sites chineses e outros que não funcionam com métodos tradicionais
    
    - **url**: URL da página para extrair meta tags
    """
    try:
        result = extract_seo_meta_tags(str(request.url))
        
        if result['status'] != 'success':
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao extrair meta tags: {result.get('error', 'Erro desconhecido')}"
            )
        
        return SEOExtractResponse(
            url=result['url'],
            title=result['title'],
            description=result['description'],
            image=result['image'],
            source=result['source'],
            status=result['status']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao extrair meta tags: {str(e)}"
        )

@app.post("/extract-product", response_model=ProductExtractResponse)
async def extract_product_endpoint(request: ProductExtractRequest):
    """
    Extrai dados COMPLETOS de um produto de e-commerce
    
    - **url**: URL do produto (Mercado Livre, Amazon, Shopee, etc.)
    
    Retorna todos os dados do produto: título, preço, imagens, descrição, etc.
    Usa Selenium para scraping robusto quando necessário.
    """
    try:
        print(f"\n📦 [API] Recebida requisição de extração de produto")
        print(f"   URL: {request.url}")
        
        # Chamar extrator principal
        result = extract_product(str(request.url))
        
        if result.status == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Erro na extração: {result.error}"
            )
        
        return ProductExtractResponse(
            url=result.url,
            platform=result.platform,
            title=result.title,
            price=result.price,
            original_price=result.original_price,
            currency=result.currency,
            description=result.description,
            images=result.images or [],
            seller=result.seller,
            rating=result.rating,
            review_count=result.review_count,
            specifications=result.specifications or {},
            extraction_method=result.extraction_method,
            status=result.status,
            error=result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [API] Erro ao extrair produto: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao extrair produto: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Endpoint de health check para Heroku"""
    return {"status": "healthy", "service": "image-extractor", "version": "2.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4000,
        reload=True
    )
