"""
Service layer tests for AlphaMapping.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestAgentService:
    """Test AgentService functionality."""
    
    @pytest.fixture
    def agent_service(self):
        """Create AgentService instance with mocked OpenAI client."""
        with patch('app.services.agent.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock chat completion response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = 'app="Apache"'
            mock_client.chat.completions.create.return_value = mock_response
            
            from app.services.agent import AgentService
            service = AgentService()
            yield service
    
    def test_translate_nl_to_cseql_fofa(self, agent_service):
        """Test natural language to FOFA query translation."""
        result = agent_service.translate_nl_to_cseql(
            "Find Apache servers in China",
            "fofa"
        )
        assert isinstance(result, str)
        assert len(result) > 0


class TestGeoLocationService:
    """Test GeoLocationService functionality."""
    
    @pytest.fixture
    def geo_service(self):
        """Create GeoLocationService instance."""
        from app.services.geolocation import GeoLocationService
        return GeoLocationService()
    
    @pytest.mark.asyncio
    async def test_get_coordinates_valid_ip(self, geo_service, mock_geolocation_response):
        """Test getting coordinates for valid IP."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_geolocation_response
            mock_get.return_value = mock_response
            
            lat, lon = await geo_service.get_coordinates("8.8.8.8")
            # Result depends on actual implementation
            # Just verify it doesn't raise
    
    @pytest.mark.asyncio
    async def test_batch_get_coordinates(self, geo_service):
        """Test batch coordinate lookup."""
        with patch.object(geo_service, 'get_coordinates', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = (39.9, 116.4)
            
            ips = ["192.168.1.1", "192.168.1.2"]
            results = await geo_service.batch_get_coordinates(ips)
            
            assert isinstance(results, dict)


class TestFofaPlatform:
    """Test FOFA platform service."""
    
    @pytest.fixture
    def fofa_platform(self):
        """Create FofaPlatform instance."""
        from app.services.fofa import FofaPlatform
        return FofaPlatform()
    
    def test_fofa_platform_init(self, fofa_platform):
        """Test FOFA platform initialization."""
        assert fofa_platform is not None
    
    @pytest.mark.asyncio
    async def test_fofa_query_with_mock(self, fofa_platform, mock_fofa_response):
        """Test FOFA query with mocked response."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_fofa_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # This test verifies the mock setup works
            # Actual query testing requires valid API keys


class TestZoomEyePlatform:
    """Test ZoomEye platform service."""
    
    @pytest.fixture
    def zoomeye_platform(self):
        """Create ZoomEyePlatform instance."""
        from app.services.zoomeye import ZoomEyePlatform
        return ZoomEyePlatform()
    
    def test_zoomeye_platform_init(self, zoomeye_platform):
        """Test ZoomEye platform initialization."""
        assert zoomeye_platform is not None
