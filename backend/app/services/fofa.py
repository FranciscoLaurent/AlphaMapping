import base64
import httpx
import logging
from typing import List, Dict, Any
from .base import BasePlatform
from ..core.config import settings

logger = logging.getLogger(__name__)


class FofaPlatform(BasePlatform):
    def __init__(self):
        self.email = settings.FOFA_EMAIL
        self.key = settings.FOFA_KEY
        self.base_url = "https://fofa.info/api/v1/search/all"

    async def query(self, query_string: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        查询 FOFA 资产。

        Args:
            query_string: FOFA 查询语法字符串
            size: 期望返回的资产数量

        Returns:
            归一化后的资产字典列表

        Raises:
            Exception: 凭证缺失、HTTP 错误、网络异常或 API 返回错误时抛出
        """
        if not self.email or not self.key:
            raise Exception("FOFA credentials not configured")

        qbase64 = base64.b64encode(query_string.encode()).decode()
        # 字段列表作为结果映射的基准
        field_list = ["ip", "port", "protocol", "domain", "host", "title", "server", "country", "city", "org"]

        params = {
            "email": self.email,
            "key": self.key,
            "qbase64": qbase64,
            "size": size,
            "fields": ",".join(field_list)
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params, timeout=30.0)
            except httpx.HTTPError as e:
                raise Exception(f"FOFA request failed: {e}")

            if response.status_code != 200:
                # 非 200 时仍尝试解析 body，优先用 API 返回的 errmsg
                try:
                    err_data = response.json()
                except Exception:
                    err_data = {}
                if err_data.get("error"):
                    raise Exception(f"FOFA API error: {err_data.get('errmsg')}")
                raise Exception(f"FOFA API HTTP error: status {response.status_code}")

            try:
                data = response.json()
            except Exception as e:
                raise Exception(f"FOFA response is not valid JSON: {e}")

            # FOFA 在 HTTP 200 下也可能通过 error 字段返回错误
            if data.get("error"):
                raise Exception(f"FOFA API error: {data.get('errmsg')}")

            raw_results = data.get("results", [])
            logger.debug(
                "[FOFA] API returned %d results, fields=%s",
                len(raw_results), data.get("fields")
            )

            # 用预定义 field_list 作为映射基准，忽略 API 实际返回的字段顺序差异
            results = [dict(zip(field_list, item_array)) for item_array in raw_results]
            return results

    def translate_nl_to_cseql(self, nl_query: str) -> str:
        # This will be handled by the Agent service
        pass
