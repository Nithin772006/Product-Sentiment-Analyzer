# Architecture

## Current Scope

This repository contains the project skeleton only. Scraping, sentiment scoring, MongoDB persistence, authentication, and deployment automation will be added in later tasks.

## Planned Flow

1. React sends a product search request to the Flask API.
2. Flask validates the request and creates a scraping job.
3. Scraper collects reviews from the selected platform.
4. Sentiment module scores each review using VADER.
5. Database module stores product, review, and sentiment records in MongoDB Atlas.
6. Dashboard endpoints aggregate stored data for charts and summary cards.

## Team Module Ownership

- Frontend team: `frontend/src`
- Backend API team: `backend/routes`, `backend/controllers`, `backend/services`
- Scraper team: `scraper`
- Sentiment team: `sentiment`
- Database team: `database`
- QA team: `tests`
- Documentation team: `docs`, `presentation`
