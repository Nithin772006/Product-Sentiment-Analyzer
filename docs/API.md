# API Contract

Base URL for local development:

```text
http://localhost:5000/api
```

## GET /health

Returns backend health status.

## POST /search

Request body:

```json
{
  "productName": "wireless headphones",
  "platform": "amazon"
}
```

Returns a placeholder job response until scraping is implemented.

## GET /reviews

Returns dummy review records that match the planned review document shape.

## GET /dashboard

Returns dummy summary metrics, sentiment distribution, rating distribution, and keywords.
