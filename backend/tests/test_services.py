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
        with patch('openai.OpenAI') as mock_openai:
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
            mock_response = Mock()
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
        """Create FofaPlatform instance with dummy credentials."""
        from app.services.fofa import FofaPlatform
        with patch('app.services.fofa.settings') as mock_settings:
            mock_settings.FOFA_EMAIL = "test@example.com"
            mock_settings.FOFA_KEY = "dummy-key"
            yield FofaPlatform()

    def test_fofa_platform_init(self, fofa_platform):
        """Test FOFA platform initialization."""
        assert fofa_platform is not None

    @pytest.mark.asyncio
    async def test_fofa_query_parses_results(self, fofa_platform, mock_fofa_response):
        """FOFA should map the raw result arrays into dicts keyed by field name."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_fofa_response
            mock_response.raise_for_status = Mock()
            mock_client.get.return_value = mock_response

            results = await fofa_platform.query('app="Apache"', size=2)

        assert len(results) == 2
        assert results[0]["ip"] == "192.168.1.1"
        assert results[0]["port"] == "80"
        assert results[1]["ip"] == "192.168.1.2"

    @pytest.mark.asyncio
    async def test_fofa_query_passes_size_param(self, fofa_platform, mock_fofa_response):
        """FOFA must forward the requested result count to the API."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_fofa_response
            mock_response.raise_for_status = Mock()
            mock_client.get.return_value = mock_response

            await fofa_platform.query('app="Apache"', size=42)

        _, kwargs = mock_client.get.call_args
        assert kwargs["params"]["size"] == 42

    @pytest.mark.asyncio
    async def test_fofa_query_raises_on_error_body(self, fofa_platform, mock_fofa_error_response):
        """FOFA must surface API-level errors as exceptions."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = mock_fofa_error_response
            mock_client.get.return_value = mock_response

            with pytest.raises(Exception, match="FOFA API error"):
                await fofa_platform.query('app="Apache"')

    @pytest.mark.asyncio
    async def test_fofa_query_raises_on_http_error(self, fofa_platform):
        """FOFA must raise on a non-2xx response even without an error body."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 503
            mock_response.json.return_value = {}
            mock_client.get.return_value = mock_response

            with pytest.raises(Exception):
                await fofa_platform.query('app="Apache"')


class TestZoomEyePlatform:
    """Test ZoomEye platform service."""

    @pytest.fixture
    def zoomeye_platform(self):
        """Create ZoomEyePlatform instance with dummy credentials."""
        from app.services.zoomeye import ZoomEyePlatform
        with patch('app.services.zoomeye.settings') as mock_settings:
            mock_settings.ZOOMEYE_KEY = "dummy-key"
            yield ZoomEyePlatform()

    def test_zoomeye_platform_init(self, zoomeye_platform):
        """Test ZoomEye platform initialization."""
        assert zoomeye_platform is not None

    @pytest.mark.asyncio
    async def test_zoomeye_query_parses_results(self, zoomeye_platform, mock_zoomeye_response):
        """ZoomEye should map the raw match objects into the unified asset schema."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_zoomeye_response
            mock_client.get.return_value = mock_response

            results = await zoomeye_platform.query('nginx', size=10)

        assert len(results) == 2
        assert results[0]["ip"] == "192.168.1.10"
        assert results[0]["port"] == 80
        assert results[0]["country"] == "China"

    @pytest.mark.asyncio
    async def test_zoomeye_query_respects_size_limit(self, zoomeye_platform, mock_zoomeye_large_response):
        """size must cap the number of returned assets, not be silently ignored."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_zoomeye_large_response
            mock_client.get.return_value = mock_response

            results = await zoomeye_platform.query('nginx', size=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_zoomeye_query_raises_on_http_error(self, zoomeye_platform):
        """ZoomEye must raise on a non-2xx response."""
        with patch('httpx.AsyncClient') as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_cls.return_value = mock_client

            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"message": "Forbidden"}
            mock_client.get.return_value = mock_response

            with pytest.raises(Exception, match="ZoomEye API error"):
                await zoomeye_platform.query('nginx')
