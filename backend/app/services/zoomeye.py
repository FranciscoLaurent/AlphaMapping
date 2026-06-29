import httpx
from typing import List, Dict, Any
from .base import BasePlatform
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

# ZoomEye /host/search 每页最多返回 20 条结果，服务端不接受 size 参数。
MAX_PER_PAGE = 20


class ZoomEyePlatform(BasePlatform):
    def __init__(self):
        self.key = settings.ZOOMEYE_KEY
        self.base_url = "https://api.zoomeye.org/host/search"

    async def query(self, query_string: str, size: int = 20) -> List[Dict[str, Any]]:
        """
        查询 ZoomEye 资产。

        ZoomEye 单次请求固定按分页返回结果，size 用于限制最终返回条数上限，
        避免上层一次拉取过多资产。

        Args:
            query_string: ZoomEye 查询语法字符串
            size: 期望返回的资产数量上限

        Returns:
            归一化后的资产字典列表
        """
        if not self.key:
            raise Exception("ZoomEye API key not configured")

        # 限制单页内可满足的数量；若超出则按需翻页累积
        size = max(1, int(size))
        page_count = (size + MAX_PER_PAGE - 1) // MAX_PER_PAGE

        headers = {"API-KEY": self.key}
        results: List[Dict[str, Any]] = []

        async with httpx.AsyncClient() as client:
            for page in range(1, page_count + 1):
                params = {
                    "query": query_string,
                    "page": page
                }

                try:
                    response = await client.get(
                        self.base_url, headers=headers, params=params, timeout=30.0
                    )
                except httpx.HTTPError as e:
                    raise Exception(f"ZoomEye request failed: {e}")

                if response.status_code != 200:
                    # 非 200 时尝试解析错误信息，避免 JSON 解析二次失败
                    try:
                        err_body = response.json()
                    except Exception:
                        err_body = {}
                    raise Exception(
                        f"ZoomEye API error: {err_body.get('message', 'Unknown error')} "
                        f"(HTTP {response.status_code})"
                    )

                try:
                    data = response.json()
                except Exception as e:
                    raise Exception(f"ZoomEye response is not valid JSON: {e}")

                matches = data.get("matches", [])
                if not matches:
                    break

                for item in matches:
                    results.append(self._normalize(item))

                # 已达到所需数量，停止翻页
                if len(results) >= size:
                    break

        # 截断到请求的 size 上限
        return results[:size]

    @staticmethod
    def _normalize(item: Dict[str, Any]) -> Dict[str, Any]:
        """将 ZoomEye 原始 match 对象归一化为统一资产 schema。"""
        portinfo = item.get("portinfo") or {}
        geoinfo = item.get("geoinfo") or {}
        return {
            "ip": item.get("ip"),
            "port": portinfo.get("port"),
            "protocol": portinfo.get("service"),
            "domain": item.get("domain"),
            "host": portinfo.get("hostname"),
            "title": portinfo.get("title"),
            "server": portinfo.get("server"),
            "country": (geoinfo.get("country") or {}).get("names", {}).get("en"),
            "city": (geoinfo.get("city") or {}).get("names", {}).get("en"),
            "org": geoinfo.get("organization")
        }

    def translate_nl_to_cseql(self, nl_query: str) -> str:
        # This will be handled by the Agent service
        pass
