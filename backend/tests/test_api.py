"""
API endpoint tests for AlphaMapping.
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test basic health/root endpoints."""
    
    def test_read_root(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data or "status" in data


class TestAssetsEndpoints:
    """Test asset-related endpoints."""
    
    def test_get_recent_assets_empty(self, client):
        """Test getting recent assets when database is empty."""
        response = client.get("/assets/recent")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_recent_assets_with_limit(self, client):
        """Test getting recent assets with custom limit."""
        response = client.get("/assets/recent?limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_asset_detail_not_found(self, client):
        """Test getting non-existent asset returns 404."""
        response = client.get("/asset/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestStatsEndpoints:
    """Test statistics endpoints."""
    
    def test_get_stats_empty_db(self, client):
        """Test stats endpoint with empty database."""
        response = client.get("/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_assets" in data
        assert data["total_assets"] == 0


class TestQueryEndpoints:
    """Test query-related endpoints."""
    
    def test_get_queries_empty(self, client):
        """Test getting queries when none exist."""
        response = client.get("/queries")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestReportEndpoints:
    """Test report-related endpoints."""
    
    def test_get_reports_empty(self, client):
        """Test getting reports when none exist."""
        response = client.get("/reports")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_download_report_not_found(self, client):
        """Test downloading non-existent report."""
        response = client.get("/download/report/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClearHistoryEndpoint:
    """Test clear history functionality."""
    
    def test_clear_history_empty_db(self, client):
        """Test clearing history when database is empty."""
        response = client.delete("/clear-history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
