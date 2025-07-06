# Agentic Insight Tracker

A full-stack application for tracking and analyzing insights from agentic tools.

## Project Structure

```
sourcegraph_tool/
├── backend/         # FastAPI backend
│   ├── app/         # Application code
│   └── requirements.txt
├── frontend/        # React TypeScript frontend
│   ├── src/         # Source code
│   └── package.json
└── requirements.txt # Python dependencies
```

## Setup Instructions

### 1. Python Environment Setup

Create and activate a virtual environment:
```bash
cd sourcegraph_tool
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Backend Setup

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: http://localhost:3000

## API Endpoints

- `GET /insights` - Retrieve insights with optional filtering
- `POST /insights` - Create new insights
- `GET /insights/trends` - Get trend data for charts
- `GET /insights/tools` - Get list of available tools

## Development

### Backend Development
- Uses FastAPI with SQLAlchemy ORM
- SQLite database for development
- Automatic API documentation at http://localhost:8000/docs

### Frontend Development
- React 18 with TypeScript
- TailwindCSS for styling
- Chart.js for data visualization
- React Router for navigation

## Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
```

Built files will be in `frontend/dist/`
