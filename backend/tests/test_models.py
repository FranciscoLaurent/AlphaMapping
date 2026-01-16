"""
Data model tests for AlphaMapping.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


class TestAssetModel:
    """Test Asset model."""
    
    def test_asset_creation(self, db_session, sample_asset_data):
        """Test creating an Asset record."""
        from app.models.models import Asset
        
        asset = Asset(**sample_asset_data)
        db_session.add(asset)
        db_session.commit()
        
        assert asset.id is not None
        assert asset.ip == sample_asset_data["ip"]
        assert asset.port == sample_asset_data["port"]
    
    def test_asset_unique_constraint(self, db_session, sample_asset_data):
        """Test that duplicate IP:Port combination raises error."""
        from app.models.models import Asset
        from sqlalchemy.exc import IntegrityError
        
        asset1 = Asset(**sample_asset_data)
        db_session.add(asset1)
        db_session.commit()
        
        # Try to add duplicate
        asset2 = Asset(**sample_asset_data)
        db_session.add(asset2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestPlatformQueryModel:
    """Test PlatformQuery model."""
    
    def test_platform_query_creation(self, db_session):
        """Test creating a PlatformQuery record."""
        from app.models.models import PlatformQuery
        
        query = PlatformQuery(
            platform="fofa",
            query_string='app="Apache"',
            nl_query="Find Apache servers",
            results_count=10
        )
        db_session.add(query)
        db_session.commit()
        
        assert query.id is not None
        assert query.platform == "fofa"
        assert query.created_at is not None


class TestSecurityReportModel:
    """Test SecurityReport model."""
    
    def test_security_report_creation(self, db_session):
        """Test creating a SecurityReport record."""
        from app.models.models import SecurityReport, PlatformQuery
        
        # Create parent query first
        query = PlatformQuery(
            platform="fofa",
            query_string='app="Apache"',
            nl_query="Find Apache servers",
            results_count=10
        )
        db_session.add(query)
        db_session.commit()
        
        # Create report
        report = SecurityReport(
            query_id=query.id,
            content="## Security Analysis\n\nTest content",
            summary="Test summary",
            risk_level="Medium"
        )
        db_session.add(report)
        db_session.commit()
        
        assert report.id is not None
        assert report.risk_level == "Medium"
