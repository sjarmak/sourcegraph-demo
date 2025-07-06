# Agentic Insight Tracker - Frontend

A React TypeScript frontend for tracking and analyzing insights from agentic tools.

## Features

- **Insights Dashboard**: View all insights in a responsive grid with filtering and search
- **Trends Analysis**: Visualize insight frequency over time with interactive charts
- **Advanced Filters**: Filter by tool, date range, and keywords
- **Responsive Design**: Works well on desktop and mobile devices

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Charts**: Chart.js with react-chartjs-2
- **Routing**: React Router DOM
- **Date Handling**: date-fns

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── components/       # Reusable UI components
│   ├── Layout.tsx   # Main layout with navigation
│   ├── InsightCard.tsx # Individual insight display
│   └── Filters.tsx  # Filter controls
├── pages/           # Page components
│   ├── Insights.tsx # Main insights dashboard
│   └── Trends.tsx   # Trends analysis page
├── services/        # API services
│   └── api.ts       # Backend API integration
├── hooks/           # Custom React hooks
│   └── useInsights.ts # Insights data fetching
├── types/           # TypeScript type definitions
│   └── index.ts     # Shared types
└── App.tsx          # Main application component
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` with the following endpoints:

- `GET /insights` - Fetch insights with optional filters
- `GET /insights/trends` - Get trend data for charts
- `GET /insights/tools` - Get list of available tools

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.
