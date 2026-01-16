import httpx
from typing import List, Dict, Any
from .base import BasePlatform
from ..core.config import settings

class ZoomEyePlatform(BasePlatform):
    def __init__(self):
        self.key = settings.ZOOMEYE_KEY
        self.base_url = "https://api.zoomeye.org/host/search"

    async def query(self, query_string: str, size: int = 20) -> List[Dict[str, Any]]:
        if not self.key:
            raise Exception("ZoomEye API key not configured")
        
        headers = {"API-KEY": self.key}
        params = {
            "query": query_string,
            "page": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, headers=headers, params=params, timeout=30.0)
            data = response.json()
            
            if response.status_code != 200:
                raise Exception(f"ZoomEye API error: {data.get('message', 'Unknown error')}")
            
            results = []
            for item in data.get("matches", []):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("portinfo", {}).get("port"),
                    "protocol": item.get("portinfo", {}).get("service"),
                    "domain": item.get("domain"),
                    "host": item.get("portinfo", {}).get("hostname"),
                    "title": item.get("portinfo", {}).get("title"),
                    "server": item.get("portinfo", {}).get("server"),
                    "country": item.get("geoinfo", {}).get("country", {}).get("names", {}).get("en"),
                    "city": item.get("geoinfo", {}).get("city", {}).get("names", {}).get("en"),
                    "org": item.get("geoinfo", {}).get("organization")
                }
                results.append(result)
            return results

    def translate_nl_to_cseql(self, nl_query: str) -> str:
        # This will be handled by the Agent service
        pass
