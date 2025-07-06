from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class InsightIngest(BaseModel):
    raw_text: str = Field(..., description="Raw text content from blogs or changelogs")


class InsightCreate(BaseModel):
    tool: str = Field(..., description="Tool name")
    date: datetime = Field(..., description="Date of the insight")
    title: str = Field(..., description="Title of the insight")
    summary: str = Field(..., description="Summary of the insight")
    topics: List[str] = Field(..., description="List of topic keywords")
    link: Optional[str] = Field(None, description="Optional link to source")
    snippet: Optional[str] = Field(None, description="Relevant content snippet for highlighting")
    matched_keywords: Optional[List[str]] = Field(None, description="Keywords that matched and caused this insight to be kept")
    source_type: Optional[str] = Field(None, description="Type of source: rss, arxiv, reddit_api, etc.")


class InsightResponse(BaseModel):
    id: int
    tool: str
    date: datetime
    title: str
    summary: str
    topics: List[str]
    link: Optional[str]
    snippet: Optional[str]
    matched_keywords: Optional[List[str]]
    source_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InsightFilter(BaseModel):
    tool: Optional[str] = Field(None, description="Filter by tool name")
    date_from: Optional[datetime] = Field(None, description="Filter from date (inclusive)")
    date_to: Optional[datetime] = Field(None, description="Filter to date (inclusive)")
    keyword: Optional[str] = Field(None, description="Filter by keyword in title or summary")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
