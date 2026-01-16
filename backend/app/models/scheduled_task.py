"""
Scheduled task model for AlphaMapping.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .models import Base
import datetime


class ScheduledTask(Base):
    """Model for scheduled data pulling tasks."""
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Task name
    nl_query = Column(String, nullable=False)  # Natural language query
    platform = Column(String, nullable=False)  # fofa or zoomeye
    cron_expression = Column(String, nullable=False)  # Cron expression (e.g., "0 2 * * *")
    is_active = Column(Boolean, default=True)  # Whether task is active
    last_run = Column(DateTime, nullable=True)  # Last execution time
    next_run = Column(DateTime, nullable=True)  # Next scheduled time
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Statistics
    run_count = Column(Integer, default=0)  # Total runs
    success_count = Column(Integer, default=0)  # Successful runs
    last_result = Column(String, nullable=True)  # Last run result message
