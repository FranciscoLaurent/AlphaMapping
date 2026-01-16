from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BasePlatform(ABC):
    @abstractmethod
    async def query(self, query_string: str, size: int = 100) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def translate_nl_to_cseql(self, nl_query: str) -> str:
        pass
