# Agentic Insight Tracker Backend

A FastAPI backend for tracking and analyzing AI agent insights from blogs and changelogs.

## Features

- **POST /api/ingest**: Accepts raw text and converts it to structured insights
- **GET /api/insights**: Retrieve insights with filtering by tool, date range, and keywords
- **GET /api/insights/tools**: Get list of unique tools
- **GET /api/insights/topics**: Get list of unique topics

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
./start.sh
```

3. Access the API at `http://localhost:8000`
4. View API documentation at `http://localhost:8000/docs`

## API Usage

### Ingest Text
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "OpenAI released GPT-4 with improved reasoning capabilities..."}'
```

### Get Insights
```bash
curl "http://localhost:8000/api/insights?tool=openai&limit=10"
```

## Database

Uses SQLite database (`insights.db`) with the following schema:
- `id`: Primary key
- `tool`: Tool name (e.g., "openai", "anthropic")
- `date`: Date of insight
- `title`: Extracted title
- `summary`: Generated summary
- `topics`: List of topic keywords (JSON)
- `link`: Optional source link
- `created_at`, `updated_at`: Timestamps
