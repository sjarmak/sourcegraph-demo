# Sourcegraph Demo - Agentic Insight Tracker

A modern full-stack web application for tracking and analyzing AI agent insights from RSS feeds and tech blogs.

## 🏗️ Application Overview

### 📊 Agentic Insight Tracker
A comprehensive web tool for monitoring the latest developments in AI agents and coding productivity tools.

**Technology Stack:**
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React 18 + TypeScript + TailwindCSS + Chart.js
- **Database**: SQLite for development

**Key Features:**
- 🔄 **RSS Feed Scraping**: Automatically monitors 15+ tech blogs and news sources
- 🤖 **AI-Powered Filtering**: Smart content filtering for AI/agent relevance
- 📈 **Real-time Analytics**: Dashboard with trend analysis and statistics
- 🎨 **Modern UI**: Responsive design with TailwindCSS
- 📊 **Data Visualization**: Interactive charts and trend analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Backend Setup
```bash
cd sourcegraph_tool/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd sourcegraph_tool/frontend
npm install
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000 - Modern React dashboard
- **Backend API**: http://localhost:8000 - FastAPI with automatic docs
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger UI

## 🎯 Current Capabilities

### Dashboard Features
- **📊 Statistics Overview**: Total insights, active sources, last update status
- **🔄 Manual Refresh**: On-demand RSS feed scraping via "Refresh Feeds" button
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **⚡ Real-time Updates**: Automatic polling during feed refresh operations

### Data Management
- **RSS Sources**: Pre-configured tech blogs and AI news sources
- **Content Filtering**: Relevance scoring for AI agent and coding productivity topics
- **Trend Analysis**: Historical data visualization and pattern recognition
- **Export Capabilities**: Data export for further analysis

### API Endpoints
- `GET /insights` - Retrieve filtered insights with pagination
- `POST /insights` - Create new insights manually
- `GET /insights/trends` - Trend data for dashboard charts
- `GET /insights/tools` - Available RSS sources and tools
- `POST /scrape` - Trigger manual RSS feed scraping
- `GET /scrape/status` - Get current scraping status

## 🛠️ Development

### Backend Development
```bash
cd sourcegraph_tool/backend
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn app.main:app --reload --port 8000

# Database migrations (if needed)
alembic upgrade head
```

### Frontend Development
```bash
cd sourcegraph_tool/frontend
# Install dependencies
npm install

# Development server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

### Code Style
- **Python**: Black formatter, FastAPI async patterns, type hints
- **TypeScript**: ESLint (react-app), Prettier, strict type checking
- **CSS**: TailwindCSS utilities, responsive design patterns

## 📁 Project Structure

```
sourcegraph-demo/
├── sourcegraph_tool/           # 🎯 Main Web Application
│   ├── backend/                # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py        # FastAPI application entry
│   │   │   ├── api.py         # API route definitions
│   │   │   ├── models.py      # SQLAlchemy database models
│   │   │   ├── database.py    # Database configuration
│   │   │   └── scraper.py     # RSS feed scraping logic
│   │   ├── insights.db        # SQLite database
│   │   └── requirements.txt   # Python dependencies
│   ├── frontend/               # React frontend
│   │   ├── src/
│   │   │   ├── components/    # Reusable UI components
│   │   │   ├── pages/         # Route pages
│   │   │   ├── services/      # API service layer
│   │   │   ├── types/         # TypeScript type definitions
│   │   │   └── App.tsx        # Main React component
│   │   ├── package.json       # Node.js dependencies
│   │   └── tailwind.config.js # TailwindCSS configuration
│   └── README.md              # Detailed setup instructions
├── AGENT.md                    # Development guidelines
└── README.md                   # This file
```

## 🚧 Current Status

### ✅ Completed Features
- Modern React frontend with TailwindCSS styling
- FastAPI backend with SQLAlchemy ORM
- RSS feed scraping and content filtering
- Real-time dashboard with statistics
- Responsive design for all screen sizes
- API documentation with Swagger UI
- Development environment setup

### 🔄 In Development
- Enhanced trend analysis visualizations
- Advanced filtering and search capabilities
- User authentication and personalization
- Export functionality for insights data
- Performance optimizations for large datasets

### 🎯 Future Enhancements
- Multi-user support with role-based access
- Integration with external APIs (GitHub, Twitter, etc.)
- Machine learning models for better content classification
- Real-time notifications for trending topics
- Advanced analytics and reporting features

## 🤝 Contributing

This is a demonstration project showcasing modern web development practices for AI/ML insight tracking applications.

### Development Guidelines
- Follow the code style guidelines in `AGENT.md`
- Ensure all changes include appropriate type hints and documentation
- Test both frontend and backend components before committing
- Use conventional commit messages for clear history

## 📄 License

This project is for demonstration purposes. 

---

**Note**: This repository demonstrates modern full-stack development practices with the Agentic Insight Tracker serving as a comprehensive example of React + FastAPI architecture for data-driven applications.
