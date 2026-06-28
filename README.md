# Product Sentiment Analyzer and Review Dashboard

A full-stack college project for collecting product reviews, running sentiment analysis, storing review data, and presenting insights through an interactive dashboard.

This repository is prepared as a team-friendly starter architecture. Scraping and sentiment analysis are intentionally left as placeholders so each module can be developed independently.

## Project Overview

The application will allow users to search for a product from supported ecommerce platforms, collect reviews, classify the reviews using NLP, store structured data in MongoDB Atlas, and display sentiment trends and review summaries in a React dashboard.

### Tech Stack

- Frontend: React.js, Axios, React Router, Chart.js
- Backend: Python, Flask, Flask REST API, Flask-CORS
- Web Scraping: Selenium, BeautifulSoup
- Sentiment Analysis: VADER
- Database: MongoDB Atlas
- Deployment: Render, Vercel
- Version Control: Git, GitHub

## Folder Structure

```text
Product-Sentiment-Analyzer/
  backend/             Flask API application
    app.py             Flask app factory and local entry point
    config.py          Environment-based backend configuration
    requirements.txt   Python dependencies
    routes/            API route registration
    controllers/       Request handlers
    models/            Data model placeholders
    services/          Business logic placeholders
  frontend/            React application
    src/
      api/             Axios client configuration
      components/      Reusable layout/UI components
      pages/           Route-level pages
      styles/          Global CSS
  scraper/             Future Selenium/BeautifulSoup scraping module
  database/            Future MongoDB connection and repository module
  sentiment/           Future VADER sentiment analysis module
  docs/                Team documentation and setup notes
  presentation/        Slides, diagrams, and demo assets
  tests/               Backend/frontend/integration test placeholders
```

## Installation

### Prerequisites

- Git
- Node.js 20 or later
- Python 3.11 or later
- MongoDB Atlas account

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

The backend will run at `http://localhost:5000`.

### Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend will run at `http://localhost:5173`.

## API Endpoints

- `GET /api/health` returns API status.
- `POST /api/search` accepts a product search request and returns dummy search metadata.
- `GET /api/reviews` returns dummy review records.
- `GET /api/dashboard` returns dummy dashboard metrics.

## Git Workflow

1. Pull the latest `main` branch before starting work.
2. Create a feature branch for your task.
3. Commit small, meaningful changes.
4. Push your branch to GitHub.
5. Open a pull request into `main`.
6. Request review from the team lead or assigned reviewer.

## Branch Strategy

- `main`: Stable project branch. Only reviewed code should be merged here.
- `frontend/<feature-name>`: Frontend pages, components, charts, and UI work.
- `backend/<feature-name>`: Flask APIs, controllers, services, and data contracts.
- `scraper/<feature-name>`: Selenium and BeautifulSoup review collection work.
- `sentiment/<feature-name>`: NLP and sentiment scoring work.
- `database/<feature-name>`: MongoDB models, repositories, and connection logic.
- `docs/<topic>`: Documentation, setup guides, and presentation updates.

Example:

```bash
git checkout -b backend/search-api
```

## Contributors

- Team Leader: Nithin
- Frontend Team:
- Backend Team:
- Scraper Team:
- Sentiment Analysis Team:
- Database Team:
- Documentation and Presentation Team:

Update this section with each teammate's name, GitHub username, and assigned module.

## Docker Readiness

This repository includes `.dockerignore` and environment templates so Docker support can be added later. Dockerfiles and Compose files are intentionally not included yet.
