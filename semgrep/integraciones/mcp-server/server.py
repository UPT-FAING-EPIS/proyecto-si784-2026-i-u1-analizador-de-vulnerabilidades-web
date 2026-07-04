import asyncio
import os
import httpx
from mcp.server.fastmcp import FastMCP

# Creamos el servidor MCP
mcp = FastMCP("Web Vulnerability Scanner")

# Variables de entorno esperadas (o URLs locales por defecto)
API_BASE_URL = os.environ.get("WVS_API_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("WVS_API_KEY", "")

@mcp.tool()
async def scan_vulnerabilities(target_url: str, depth: int = 1) -> str:
    """Escanea una URL en busca de vulnerabilidades web (XSS, SQLi, cabeceras faltantes, etc)."""
    if not API_KEY:
        return "Error: La variable de entorno WVS_API_KEY no está configurada."
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"target_url": target_url, "depth": depth}
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Iniciar el escaneo de forma asíncrona
            response = await client.post(f"{API_BASE_URL}/api/integrations/scans", json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            scan_data = response.json()
            scan_id = scan_data["id"]
            
            # 2. Polling: esperar hasta que termine el escaneo
            while True:
                await asyncio.sleep(3)
                res_detail = await client.get(f"{API_BASE_URL}/api/integrations/scans/{scan_id}", headers=headers, timeout=10.0)
                res_detail.raise_for_status()
                detail = res_detail.json()
                
                if detail["status"] in ["completed", "failed"]:
                    break
                    
            if detail["status"] == "failed":
                return f"El escaneo falló por un error interno: {detail.get('error_message')}"
                
            # 3. Formatear y retornar los resultados a Claude
            vulns = detail.get("vulnerabilities", [])
            if not vulns:
                return f"✅ Escaneo completado. No se encontraron vulnerabilidades en {target_url}."
                
            report = f"⚠️ Se encontraron {len(vulns)} vulnerabilidades en {target_url} (Puntuación de Riesgo: {detail.get('risk_score')}/100):\n\n"
            for v in vulns:
                report += f"- [{v['severity'].upper()}] {v['title']}: {v['description']}\n  Recomendación: {v['remediation']}\n\n"
                
            return report
            
        except Exception as e:
            return f"Error al comunicarse con el servidor del Scanner: {str(e)}"

if __name__ == "__main__":
    # Inicia el servidor usando Standard IO (el transporte estándar para MCP)
    mcp.run(transport='stdio')
