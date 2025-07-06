from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    tool = Column(String, index=True, nullable=False)
    date = Column(DateTime, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    topics = Column(JSON, nullable=False)  # List of topic strings
    link = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)  # Relevant content snippet for highlighting
    matched_keywords = Column(JSON, nullable=True)  # List of matched keywords that caused this insight to be kept
    source_type = Column(String, nullable=True)  # Type of source: rss, arxiv, reddit_api, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_insights_tool_link', 'tool', 'link', unique=True),  # Prevent duplicates
    )
