from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    port = Column(Integer)
    protocol = Column(String)
    domain = Column(String, index=True)
    host = Column(String)
    title = Column(String)
    server = Column(String)
    country = Column(String)
    city = Column(String)
    org = Column(String)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    platform = Column(String) # fofa, zoomeye
    raw_data = Column(JSON)
    query_id = Column(Integer, ForeignKey("platform_queries.id"))
    # Geolocation data
    latitude = Column(String)  # Store as string for precision
    longitude = Column(String)
    
    # Unique constraint on ip:port combination
    __table_args__ = (
        UniqueConstraint('ip', 'port', name='uix_ip_port'),
    )

class PlatformQuery(Base):
    __tablename__ = "platform_queries"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)
    query_string = Column(String)
    nl_query = Column(String) # Natural language that generated this
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    results_count = Column(Integer)
    assets = relationship("Asset", backref="query")

class SecurityReport(Base):
    __tablename__ = "security_reports"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("platform_queries.id"))
    content = Column(Text)
    summary = Column(String)
    risk_level = Column(String) # High, Medium, Low
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)  # Path to saved report file
