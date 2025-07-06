from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

from app.db import get_db
from app.models import Insight
from app.schemas import InsightIngest, InsightCreate, InsightResponse, InsightFilter
from app.core import TextProcessor
from app.core.rss_scraper import RSSFeedScraper
from app.core.source_manager import SourceManager

router = APIRouter(prefix="/api", tags=["insights"])


@router.post("/ingest", response_model=InsightResponse)
async def ingest_insight(
    ingest_data: InsightIngest,
    db: Session = Depends(get_db)
) -> InsightResponse:
    """
    Ingest raw text and convert it to a structured insight.
    """
    try:
        # Process the raw text
        processor = TextProcessor()
        insight_data = processor.extract_insight(ingest_data.raw_text)
        
        # Generate snippet for highlighting
        snippet = processor.extract_relevant_snippet(ingest_data.raw_text)
        
        # Create database record
        db_insight = Insight(
            tool=insight_data.tool,
            date=insight_data.date,
            title=insight_data.title,
            summary=insight_data.summary,
            topics=insight_data.topics,
            link=insight_data.link,
            snippet=snippet,
            matched_keywords=getattr(insight_data, 'matched_keywords', None),
            source_type=getattr(insight_data, 'source_type', None)
        )
        
        db.add(db_insight)
        db.commit()
        db.refresh(db_insight)
        
        return InsightResponse.model_validate(db_insight)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing insight: {str(e)}")


@router.get("/insights", response_model=List[InsightResponse])
async def get_insights(
    tool: str = Query(None, description="Filter by tool name"),
    sources: str = Query(None, description="Comma-separated list of sources to filter by"),
    date_from: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: str = Query(None, description="Filter to date (YYYY-MM-DD)"),
    from_hours: int = Query(None, description="Hours back from now (alternative to date_from/date_to)"),
    keyword: str = Query(None, description="Filter by keyword in title or summary"),
    q: str = Query(None, description="Full-text search query"),
    tags: str = Query(None, description="Comma-separated list of tags to filter by"),
    matched_keywords: str = Query(None, description="Comma-separated list of matched keywords to filter by"),
    source_type: str = Query(None, description="Filter by source type (rss, arxiv, etc.)"),
    limit: int = Query(500, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
) -> List[InsightResponse]:
    """
    Get insights with optional filtering and search.
    """
    try:
        # Build query
        query = db.query(Insight)
        
        # Apply filters
        conditions = []
        
        # Tool/source filtering
        if tool:
            conditions.append(Insight.tool == tool)
        
        if sources:
            source_list = [s.strip() for s in sources.split(',')]
            conditions.append(Insight.tool.in_(source_list))
        
        # Date filtering with default 30-day window
        if from_hours:
            cutoff_time = datetime.now() - timedelta(hours=from_hours)
            conditions.append(Insight.date >= cutoff_time)
        else:
            if date_from:
                date_from_dt = datetime.fromisoformat(date_from)
                conditions.append(Insight.date >= date_from_dt)
            
            if date_to:
                date_to_dt = datetime.fromisoformat(date_to)
                conditions.append(Insight.date <= date_to_dt)
            
            # Default to last 30 days if no date filters specified
            if not date_from and not date_to:
                cutoff_time = datetime.now() - timedelta(days=30)
                conditions.append(Insight.date >= cutoff_time)
        
        # Enhanced full-text search across all relevant fields
        if q:
            search_condition = or_(
                Insight.title.ilike(f"%{q}%"),
                Insight.summary.ilike(f"%{q}%"),
                Insight.snippet.ilike(f"%{q}%"),
                Insight.tool.ilike(f"%{q}%"),
                Insight.matched_keywords.ilike(f'%"{q.lower()}"%'),  # JSON LIKE search
                Insight.topics.ilike(f'%"{q.lower()}"%')  # JSON LIKE search
            )
            conditions.append(search_condition)
        
        # Backward compatibility for keyword
        if keyword and not q:
            keyword_condition = or_(
                Insight.title.ilike(f"%{keyword}%"),
                Insight.summary.ilike(f"%{keyword}%")
            )
            conditions.append(keyword_condition)
        
        # Tag filtering (SQLite-compatible JSON search)
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            for tag in tag_list:
                # Use LIKE with JSON for SQLite compatibility
                conditions.append(Insight.topics.ilike(f'%"{tag}"%'))
        
        # Matched keywords filtering (SQLite-compatible JSON search)
        if matched_keywords:
            keyword_list = [kw.strip() for kw in matched_keywords.split(',')]
            for kw in keyword_list:
                # Use LIKE with JSON for SQLite compatibility
                conditions.append(Insight.matched_keywords.ilike(f'%"{kw}"%'))
        
        # Source type filtering
        if source_type:
            conditions.append(Insight.source_type == source_type)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Apply pagination and ordering
        insights = query.order_by(Insight.date.desc()).offset(offset).limit(limit).all()
        
        return [InsightResponse.model_validate(insight) for insight in insights]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving insights: {str(e)}")


@router.get("/insights/tools", response_model=List[str])
async def get_tools(db: Session = Depends(get_db)) -> List[str]:
    """
    Get list of all unique tools/sources.
    """
    try:
        tools = db.query(Insight.tool).distinct().all()
        return [tool[0] for tool in tools]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")


@router.get("/insights/sources", response_model=List[str])
async def get_sources() -> List[str]:
    """
    Get list of all configured sources.
    """
    try:
        source_manager = SourceManager()
        return source_manager.get_source_names()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sources: {str(e)}")


@router.get("/insights/keywords", response_model=List[str])
async def get_keywords(db: Session = Depends(get_db)) -> List[str]:
    """
    Get list of all unique matched keywords.
    """
    try:
        # Get all unique matched keywords from the database
        insights = db.query(Insight.matched_keywords).filter(
            Insight.matched_keywords.isnot(None)
        ).all()
        
        all_keywords = set()
        for insight in insights:
            if insight.matched_keywords:
                all_keywords.update(insight.matched_keywords)
        
        return sorted(list(all_keywords))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving keywords: {str(e)}")


@router.get("/insights/source-types", response_model=List[str])
async def get_source_types(db: Session = Depends(get_db)) -> List[str]:
    """
    Get list of all unique source types.
    """
    try:
        source_types = db.query(Insight.source_type).distinct().filter(
            Insight.source_type.isnot(None)
        ).all()
        return [st[0] for st in source_types if st[0]]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving source types: {str(e)}")


@router.get("/insights/topics", response_model=List[str])
async def get_topics(db: Session = Depends(get_db)) -> List[str]:
    """
    Get list of all unique topics.
    """
    try:
        insights = db.query(Insight.topics).all()
        all_topics = set()
        for insight in insights:
            if insight.topics:
                all_topics.update(insight.topics)
        return sorted(list(all_topics))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving topics: {str(e)}")


@router.get("/insights/trends")
async def get_trends(
    period: str = Query("7d", description="Time period: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Get trends data for charts.
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.now()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get insights in the date range
        insights = db.query(Insight).filter(
            Insight.date >= start_date,
            Insight.date <= end_date
        ).all()
        
        # Group by date and tool
        from collections import defaultdict
        trend_data = defaultdict(lambda: defaultdict(int))
        
        for insight in insights:
            date_str = insight.date.strftime("%Y-%m-%d")
            trend_data[date_str][insight.tool] += 1
        
        # Convert to the expected format
        result = []
        for date_str, tools in trend_data.items():
            for tool, count in tools.items():
                result.append({
                    "date": date_str,
                    "tool": tool,
                    "count": count
                })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trends: {str(e)}")


@router.post("/scrape-feeds")
async def scrape_feeds(
    background_tasks: BackgroundTasks,
    hours_back: int = Query(24, description="Hours back to scrape"),
    sources: str = Query(None, description="Comma-separated list of sources to scrape"),
    db: Session = Depends(get_db)
):
    """
    Trigger feed scraping using the new source manager.
    """
    try:
        source_manager = SourceManager()
        
        # Parse sources if provided
        source_list = None
        if sources:
            source_list = [s.strip() for s in sources.split(',')]
        
        # Run scraping in background
        def run_scraper():
            import asyncio
            result = asyncio.run(source_manager.scrape_all_sources(db, hours_back, source_list))
            return result
        
        background_tasks.add_task(run_scraper)
        
        return {"message": "Feed scraping started", "status": "started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting feed scraping: {str(e)}")


@router.get("/scrape-feeds/status")
async def get_scrape_status(db: Session = Depends(get_db)):
    """
    Get the status of recent RSS feed scraping.
    """
    try:
        from datetime import datetime, timedelta
        
        # Get insights from last 24 hours
        recent_insights = db.query(Insight).filter(
            Insight.created_at >= datetime.now() - timedelta(hours=24)
        ).all()
        
        # Group by tool
        from collections import defaultdict
        tool_counts = defaultdict(int)
        
        for insight in recent_insights:
            tool_counts[insight.tool] += 1
        
        return {
            "total_insights_24h": len(recent_insights),
            "insights_by_tool": dict(tool_counts),
            "last_updated": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scrape status: {str(e)}")
