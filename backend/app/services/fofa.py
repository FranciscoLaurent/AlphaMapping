import base64
import httpx
from typing import List, Dict, Any
from .base import BasePlatform
from ..core.config import settings

class FofaPlatform(BasePlatform):
    def __init__(self):
        self.email = settings.FOFA_EMAIL
        self.key = settings.FOFA_KEY
        self.base_url = "https://fofa.info/api/v1/search/all"

    async def query(self, query_string: str, size: int = 10) -> List[Dict[str, Any]]:
        if not self.email or not self.key:
            raise Exception("FOFA credentials not configured")
        
        qbase64 = base64.b64encode(query_string.encode()).decode()
        # Use a predefined fields list
        field_list = ["ip", "port", "protocol", "domain", "host", "title", "server", "country", "city", "org"]
        
        params = {
            "email": self.email,
            "key": self.key,
            "qbase64": qbase64,
            "size": size,
            "fields": ",".join(field_list)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, timeout=30.0)
            data = response.json()
            
            if data.get("error"):
                raise Exception(f"FOFA API error: {data.get('errmsg')}")
            
            # Parse results
            results = []
            api_fields = data.get("fields", [])
            raw_results = data.get("results", [])
            
            print(f"[FOFA] API returned {len(raw_results)} results")
            print(f"[FOFA] Fields from API: {api_fields}")
            print(f"[FOFA] Expected fields: {field_list}")
            
            for item_array in raw_results:
                # Map array values to field names
                # Use our predefined field_list as the source of truth
                result_dict = dict(zip(field_list, item_array))
                results.append(result_dict)
                
            if results and len(results) > 0:
                print(f"[FOFA] Sample mapped result: {results[0]}")
            
            return results

    def translate_nl_to_cseql(self, nl_query: str) -> str:
        # This will be handled by the Agent service
        pass
