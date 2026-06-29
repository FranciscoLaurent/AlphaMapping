import httpx
from typing import Optional, Dict, Tuple
from ..core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class GeoLocationService:
    """
    Service for IP geolocation using ip-api.com.
    Includes caching to avoid repeated requests.
    """
    
    def __init__(self):
        self.cache: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
        self.api_url = settings.IP_GEOLOCATION_API
        
    async def get_coordinates(self, ip: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get latitude and longitude for an IP address.
        
        Args:
            ip: IP address string
            
        Returns:
            Tuple of (latitude, longitude) as strings, or (None, None) if lookup fails
        """
        if not ip or ip == "N/A":
            return None, None
            
        # Check cache first
        if ip in self.cache:
            return self.cache[ip]
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.api_url}{ip}",
                    params={"fields": "status,lat,lon"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        raw_lat = data.get("lat")
                        raw_lon = data.get("lon")
                        # None / 空值不转字符串，避免存 "None" 导致 float() 崩溃
                        if raw_lat is not None and raw_lon is not None:
                            lat = str(raw_lat)
                            lon = str(raw_lon)
                            self.cache[ip] = (lat, lon)
                            return lat, lon
                        
        except Exception as e:
            logger.warning(f"Failed to get geolocation for {ip}: {e}")
        
        # Cache failures to avoid repeated requests
        self.cache[ip] = (None, None)
        return None, None
    
    async def batch_get_coordinates(self, ips: list) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
        """
        Get coordinates for multiple IPs concurrently.
        
        Args:
            ips: List of IP addresses
            
        Returns:
            Dictionary mapping IP to (latitude, longitude) tuple
        """
        # Filter out already cached IPs
        unique_ips = list(set(ips))
        uncached_ips = [ip for ip in unique_ips if ip not in self.cache]
        
        # Fetch uncached IPs with rate limiting (max 45 requests/minute for ip-api.com free tier)
        tasks = []
        for ip in uncached_ips:
            tasks.append(self.get_coordinates(ip))
            # Rate limiting: small delay between requests
            if len(tasks) % 10 == 0:
                await asyncio.sleep(0.5)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Return all results from cache
        return {ip: self.cache.get(ip, (None, None)) for ip in unique_ips}
