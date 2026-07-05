"""
Rutas API para generar soluciones automáticas con IA
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
from ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/solutions", tags=["solutions"])


class GenerateSolutionRequest(BaseModel):
    """Modelo para solicitud de generación de solución"""
    vulnerability_type: str
    target_stack: str = "generic"
    use_cache: bool = True


class GenerateMultipleSolutionsRequest(BaseModel):
    """Modelo para generar múltiples soluciones"""
    vulnerabilities: List[dict]


@router.post("/generate")
async def generate_solution(request: GenerateSolutionRequest):
    """
    Genera solución automática para vulnerabilidad usando IA
    
    Ejemplo:
    {
        "vulnerability_type": "XSS",
        "target_stack": "node"
    }
    """
    try:
        solution = ai_service.generate_solution(
            vulnerability_type=request.vulnerability_type,
            target_stack=request.target_stack,
            use_cache=request.use_cache
        )
        
        if not solution.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=solution.get("error", "Error generando solución")
            )
        
        return solution
    
    except Exception as e:
        logger.error(f"Error en generate_solution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando solución: {str(e)}"
        )


@router.post("/generate-multiple")
async def generate_multiple_solutions(request: GenerateMultipleSolutionsRequest):
    """
    Genera soluciones para múltiples vulnerabilidades
    
    Ejemplo:
    {
        "vulnerabilities": [
            {"type": "XSS", "stack": "node"},
            {"type": "SQLi", "stack": "python"},
            {"type": "CSRF", "stack": "php"}
        ]
    }
    """
    try:
        results = ai_service.generate_multiple(request.vulnerabilities)
        return results
    
    except Exception as e:
        logger.error(f"Error en generate_multiple_solutions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando soluciones: {str(e)}"
        )


@router.get("/available-stacks")
async def get_available_stacks():
    """Retorna lista de stacks soportados"""
    return {
        "stacks": [
            "node",
            "python",
            "php",
            "java",
            "dotnet",
            "nginx",
            "apache",
            "generic"
        ]
    }


@router.get("/cache-status")
async def get_cache_status():
    """Retorna estado del caché de soluciones"""
    return {
        "cache_size": len(ai_service.cache),
        "cached_solutions": list(ai_service.cache.keys())
    }


@router.post("/cache-clear")
async def clear_cache():
    """Limpia el caché de soluciones"""
    ai_service.clear_cache()
    return {"message": "Caché limpiado", "success": True}
