# Agent Guide for Planet Express Demo

## Quick Start Commands
- **Start dev:** `./start_local.sh` (starts both backend and frontend)
- **Test Python:** `pytest backend/tests/` or `python -m pytest backend/tests/`
- **Test single:** `pytest backend/tests/test_specific.py::test_function`
- **Format:** `black .` and `ruff --fix .`
- **Type check:** `mypy backend/`
- **Frontend test:** `cd frontend && npm test`
- **Build frontend:** `cd frontend && npm run build`
- **Backend only:** `cd backend && python -m uvicorn app.main:app --reload --port 8000`

## Architecture Overview
Multi-service ADS (Astrophysics Data System) ecosystem:
- **search-comparisons**: FastAPI backend + React frontend for multi-engine academic search ⚠️ **EDITABLE**
- **ADSMasterPipeline**: Data pipeline coordinating bibliographic/metrics/fulltext processing 📖 **READ-ONLY**
- **montysolr**: Custom Solr-based search engine with powerful query parser 📖 **READ-ONLY**
- **adsabs-dev-api**: Developer API documentation and examples 📖 **READ-ONLY**
- **solr-service**: Microservice proxy for Solr operations 📖 **READ-ONLY**

## ⚠️ IMPORTANT: Edit Restrictions
**ONLY make changes to files in the `search-comparisons/` directory.** All other ADS repos are for context only - read them to understand APIs, data structures, and integration patterns, but DO NOT edit them. When implementing features, focus on the search-comparisons backend/frontend.

## Code Style
- **Python**: Black formatter, Ruff linter, type hints required, FastAPI async patterns
- **JavaScript**: ESLint (react-app), async/await preferred, Material-UI components
- **Imports**: Absolute imports, group stdlib/third-party/local
- **Naming**: snake_case (Python), camelCase (JS), descriptive variable names
- **Error handling**: Proper exception handling, structured logging, graceful fallbacks
