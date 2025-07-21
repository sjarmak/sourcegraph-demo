# Agent Guide for Agentic Insight Tracker

## Quick Start Commands

### Backend
- **Start dev:** `cd backend && source ../venv/bin/activate && nohup python -m uvicorn app.main:app --reload --port 8000 > server.log 2>&1 &`
- **Start dev (simple):** `cd backend && python -m uvicorn app.main:app --reload --port 8000` (blocks terminal)
- **Full setup:** `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- **Test manually:** `python backend/test_enhanced_api.py` (comprehensive API tests)
- **Test RSS feeds:** `python backend/test_rss_feeds.py` (validates all feed sources)
- **Test search:** `python backend/test_search_fixes.py` (search functionality)

### Frontend  
- **Start dev:** `cd frontend && nohup npm run dev > frontend.log 2>&1 &` (detached, port 3000)
- **Start dev (simple):** `cd frontend && npm run dev` (blocks terminal)
- **Install deps:** `cd frontend && npm install`
- **Build:** `cd frontend && npm run build`
- **Lint:** `cd frontend && npm run lint`
- **Test connection:** `node test_frontend.js` (basic API connectivity test)

### Combined
- **Full dev setup:** Start backend on :8000, then frontend on :3000

## Project Architecture

**Purpose:** Full-stack application for tracking and analyzing insights from AI agent tools via RSS feeds and manual ingestion.

```
sourcegraph_tool/
├── backend/              # FastAPI backend (Python 3.11+)
│   ├── app/
│   │   ├── api/         # REST API endpoints (/insights, /trends, /tools)
│   │   ├── core/        # RSS scraping, text processing, ingestion
│   │   ├── db/          # SQLAlchemy database session management
│   │   ├── models/      # SQLAlchemy ORM models (Insight, etc.)
│   │   └── schemas/     # Pydantic request/response schemas
│   └── insights.db      # SQLite database (dev)
├── frontend/             # React 18 + TypeScript + Vite
│   ├── src/             # React components, pages, utilities
│   └── dist/            # Production build output
└── venv/                # Python virtual environment
```

**Data Flow:**
1. RSS feeds configured in `core/sources.json` → `RSSFeedScraper`
2. Content processing → `TextProcessor` → SQLite database
3. React frontend fetches via `/api/insights` and `/api/insights/trends`
4. Visualization using Chart.js and TailwindCSS

## API Endpoints

- `GET /insights` - Retrieve insights with filtering (tool, date range, keywords)
- `POST /insights` - Create new insights manually
- `GET /insights/trends` - Trend data for Chart.js visualization
- `GET /insights/tools` - List of available AI tools tracked
- `GET /health` - Health check endpoint

## Tech Stack

### Backend
- **FastAPI** - Async web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0** - ORM with async support  
- **Pydantic v2** - Data validation and serialization
- **SQLite** - Development database (easily switchable to PostgreSQL)
- **aiohttp/feedparser** - RSS feed scraping and parsing

### Frontend  
- **React 18** - UI framework with concurrent features
- **TypeScript** - Type safety throughout
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first styling
- **Chart.js + react-chartjs-2** - Data visualization
- **React Router v7** - Client-side routing
- **Lucide React** - Icon library

## Code Style & Conventions

### Python (Backend)
- **Async/await patterns** - Use `async def` for I/O operations
- **Type hints required** - Leverage Pydantic for validation
- **Import organization** - Standard library, third-party, local imports
- **Error handling** - Structured logging, graceful fallbacks
- **API documentation** - Available at http://localhost:8000/docs

### TypeScript (Frontend)
- **Strict TypeScript** - `strict: true` in tsconfig
- **React hooks patterns** - Functional components with hooks
- **ESLint + React rules** - Configured with react-hooks plugin
- **Component structure** - Props interfaces, default exports
- **Async operations** - fetch with error boundaries

## Testing Strategy

### Current Testing (Manual Scripts)
- `backend/test_enhanced_api.py` - Comprehensive API endpoint testing
- `backend/test_rss_feeds.py` - RSS feed availability and parsing validation
- `backend/test_sourcegraph_feed.py` - Specific Sourcegraph feed testing
- `backend/test_search_fixes.py` - Search and pagination functionality
- `backend/test_enhanced_ingestion.py` - Content ingestion pipeline testing
- `test_frontend.js` - Basic frontend-backend connectivity test

### Recommended Testing Framework Migration
- **Backend:** Migrate to `pytest` + `pytest-asyncio` with FastAPI TestClient
- **Frontend:** Add `vitest` + `@testing-library/react` for component testing
- **Integration:** API testing with in-memory SQLite for isolation

## Database Management

### Current Approach
- SQLite database (`insights.db`) for development
- Manual migration scripts: `migrate_database.py`, `migrate_database_v2.py`
- Schema includes: insights table with metadata, keywords, source tracking

### Production Considerations
- Switch to PostgreSQL via `DATABASE_URL` environment variable
- Consider Alembic for proper migration management
- Database connection pooling for concurrent requests

## Agent Guidelines

### Long-Running Commands
**ALWAYS detach long-running commands by default** using `nohup command > logfile.log 2>&1 &`. This includes:
- Starting development servers (backend, frontend)
- Any command that blocks the terminal
- Build/watch processes

Only use blocking commands when user explicitly requests it or for testing.

## Development Workflow

1. **Feature Development**
   - Start backend: `cd backend && source ../venv/bin/activate && nohup python -m uvicorn app.main:app --reload --port 8000 > server.log 2>&1 &`
   - Start frontend: `cd frontend && nohup npm run dev > frontend.log 2>&1 &`
   - API docs available at: http://localhost:8000/docs

2. **Testing Changes**
   - Run manual test suite: `python backend/test_enhanced_api.py`
   - Test RSS integration: `python backend/test_rss_feeds.py`
   - Frontend connectivity: `node test_frontend.js`

3. **Adding New Features**
   - RSS Sources: Update `backend/app/core/sources.json`
   - API Endpoints: Add to `backend/app/api/`
   - Frontend Components: Add to `frontend/src/components/`
   - Database Changes: Create migration script

## Environment Variables

- `DATABASE_URL` - Database connection (default: SQLite)
- `CORS_ORIGINS` - Allowed origins for CORS (default: "*")
- `UVICORN_HOST` - Server host (default: "127.0.0.1")
- `UVICORN_PORT` - Server port (default: 8000)

## Deployment

### Backend Production
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Production  
```bash
cd frontend
npm run build
# Serve dist/ with nginx or include in FastAPI static files
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Set proper `CORS_ORIGINS` or use "*" for development |
| Database locked | Use single-threaded server or switch to PostgreSQL |
| Port conflicts | Change backend port with `--port` flag |
| Missing dependencies | Run `pip install -r requirements.txt` and `npm install` |
| RSS feed failures | Check `rss_feed_test_report.txt` for feed status |

## Key Files to Know

- [`backend/app/main.py`](backend/app/main.py) - FastAPI application entry point
- [`backend/app/api/`](backend/app/api/) - All REST API endpoints
- [`backend/app/core/sources.json`](backend/app/core/sources.json) - RSS feed configuration  
- [`frontend/src/App.tsx`](frontend/src/App.tsx) - React application root
- [`frontend/package.json`](frontend/package.json) - Frontend dependencies and scripts
- [`requirements.txt`](requirements.txt) - Python dependencies
