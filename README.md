# SlayCrawl

A modern, async web scraping API built with FastAPI, Redis, and Playwright. Provides powerful web scraping capabilities with JavaScript rendering support, caching, and customizable data extraction.

## Features

- 🚀 Fast async web scraping with FastAPI
- 🎭 JavaScript rendering support via Playwright
- 📦 Redis caching for improved performance
- 🔑 API key authentication
- 🔄 Hot reload during development
- 🎯 Health monitoring dashboard
- 📝 SQLite database for data persistence
- 🐳 Docker support with docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git (optional)

### Installation & Setup

1. Clone the repository (or download the source code):
```bash
git clone https://github.com/yourusername/slaycrawl.git
cd slaycrawl
```

2. Create a `.env` file in the project root:
```bash
REDIS_URL=redis://redis:6379
LOG_LEVEL=INFO
API_KEY="your_api_key_here"
```

3. Start the application:
```bash
docker-compose up --build
```

The application will be available at:
- Main UI: http://localhost:8000
- Health Dashboard: http://localhost:8000/health-ui
- API Documentation: http://localhost:8000/docs

### Development with Hot Reload

The application is configured with hot reload by default. Any changes you make to the Python files in the `app` directory will automatically trigger a reload of the application.

To test the hot reload:
1. Make sure the application is running (`docker-compose up`)
2. Edit any file in the `app` directory
3. The application will automatically reload with your changes

## Testing the API

### 1. Create an API Key

```bash
curl -X POST "http://localhost:8000/api/keys" \
     -H "Content-Type: application/json" \
     -d '{"name": "test-key", "description": "Testing key"}'
```

### 2. Test Web Scraping

```bash
# Replace YOUR_API_KEY with the key from step 1
curl -X POST "http://localhost:8000/scrape" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{"url": "https://example.com", "render_js": true}'
```

### 3. Check System Health

```bash
# Via curl
curl http://localhost:8000/health

# Or visit the health dashboard
open http://localhost:8000/health-ui
```

## Project Structure

```
slaycrawl/
├── app/
│   ├── static/          # Static files (HTML, CSS, JS)
│   ├── __init__.py
│   ├── main.py         # FastAPI application
│   ├── scraper.py      # Web scraping logic
│   ├── cache.py        # Redis cache implementation
│   ├── database.py     # Database models and connection
│   ├── models.py       # Pydantic models
│   ├── security.py     # Authentication logic
│   └── worker.py       # Background task worker
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Development Commands

```bash
# Start the application
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Stop the application
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Check if Redis container is running: `docker-compose ps`
   - Verify Redis URL in `.env` file
   - Check Redis logs: `docker-compose logs redis`

2. **Database Issues**
   - Check if database file exists
   - Verify permissions on the data directory
   - Check application logs: `docker-compose logs api`

3. **Hot Reload Not Working**
   - Ensure volumes are properly mounted in `docker-compose.yml`
   - Check if the file changes are in the `app` directory
   - Verify uvicorn is running with `--reload` flag

### Health Check

The application includes a health check system that monitors:
- Overall application status
- Redis connection
- Database connection

Visit http://localhost:8000/health-ui to view the health dashboard.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📚 [API Documentation](http://localhost:8000/docs)
- 🐛 [Issue Tracker](https://github.com/yourusername/slaycrawl/issues)
- 💬 [Discussions](https://github.com/yourusername/slaycrawl/discussions)

## Acknowledgments

- Built with FastAPI, Redis, and Playwright
- Inspired by the need for a modern, async web scraping solution
# SlayCrawl API

A modern, async web scraping API built with FastAPI, Redis, and Playwright. Slay those web pages with style! 💅

## Features

- ⚡ **Async Everything**: Built with FastAPI and HTTPX for lightning-fast performance
- 🎭 **Smart JS Rendering**: Uses Playwright for JavaScript-heavy sites
- 🗃️ **Redis Caching**: Blazing fast response times for repeat requests
- 🔍 **Custom Selectors**: Extract exactly what you need with CSS selectors
- 📝 **Multiple Output Formats**: Get your data in JSON or Markdown
- 🚀 **Background Crawling**: Handle large sites with async job processing
- 🛡️ **Anti-Bot Ready**: Built-in user agent rotation and proxy support (coming soon)

## Prerequisites

Before you begin, ensure you have:
- Docker and Docker Compose installed
- Python 3.11 or higher (for local development)
- Git

## Quick Start with Docker

1. Clone the repo:
```bash
git clone https://github.com/yourusername/slaycrawl.git
cd slaycrawl
```

2. Create a `.env` file with your configuration:
```bash
# Required settings
REDIS_URL=redis://redis:6379
API_KEY_SECRET=your-secret-key  # Change this in production!

# Optional settings
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
CACHE_EXPIRY=3600              # Cache expiry in seconds
MAX_CONCURRENT_SCRAPES=10       # Maximum concurrent scraping jobs
```

3. Run with Docker Compose:
```bash
# Development mode with hot reload
docker-compose up -d

# Production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The API will be available at:
- API Endpoint: `http://localhost:8000`
- Interactive API Documentation: `http://localhost:8000/docs`
- Alternative API Documentation: `http://localhost:8000/redoc`

## Local Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
playwright install-deps
```

4. Start Redis (required for caching):
```bash
docker-compose up -d redis
```

5. Run the development server with hot reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage Guide

### Authentication

All API endpoints (except documentation) require an API key. You can manage API keys through the following endpoints:

1. Create a new API key:
```bash
curl -X POST http://localhost:8000/api/keys \
  -H "Content-Type: application/json" \
  -d '{"name": "My Scraper", "description": "For testing purposes"}'
```

2. Use the API key in requests:
```bash
curl -X POST http://localhost:8000/scrape \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "render_js": true
  }'
```

### Scraping Endpoints

#### Single Page Scraping

```http
POST /scrape
```

Request body:
```json
{
    "url": "https://example.com",
    "render_js": false,
    "output_format": "json",
    "selectors": {
        "title": "h1",
        "content": "article p",
        "links": "a[href]"
    },
    "wait_for": ".content-loaded",  // Optional: wait for element
    "timeout": 30000               // Optional: timeout in ms
}
```

Response:
```json
{
    "url": "https://example.com",
    "title": "Example Domain",
    "content": ["Paragraph 1", "Paragraph 2"],
    "links": [
        {"text": "Link 1", "href": "https://example.com/1"},
        {"text": "Link 2", "href": "https://example.com/2"}
    ],
    "timestamp": "2024-04-04T10:20:30Z",
    "cached": false
}
```

#### Batch Scraping

```http
POST /scrape/batch
```

Request body:
```json
{
    "urls": [
        "https://example.com/1",
        "https://example.com/2"
    ],
    "render_js": false,
    "concurrent_limit": 5
}
```

### Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid/missing API key)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

Error response format:
```json
{
    "detail": "Error message here",
    "code": "ERROR_CODE",
    "timestamp": "2024-04-04T10:20:30Z"
}
```

## Configuration Options

All configuration can be set via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://redis:6379` |
| `API_KEY_SECRET` | Secret for API key generation | Required |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `CACHE_EXPIRY` | Cache TTL in seconds | `3600` |
| `MAX_CONCURRENT_SCRAPES` | Concurrent scrape limit | `10` |
| `PLAYWRIGHT_TIMEOUT` | Browser timeout in ms | `30000` |

## Contributing

1. Fork the repository
2. Create your feature branch:
```bash
git checkout -b feature/amazing-feature
```

3. Set up development environment as described above

4. Make your changes and add tests if applicable

5. Run tests:
```bash
pytest
```

6. Commit your changes:
```bash
git commit -m 'Add amazing feature'
```

7. Push to your fork and submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📚 [API Documentation](http://localhost:8000/docs)
- 🐛 [Issue Tracker](https://github.com/yourusername/slaycrawl/issues)
- 💬 [Discussions](https://github.com/yourusername/slaycrawl/discussions)

## Acknowledgments

- Built with FastAPI, Redis, and Playwright
- Inspired by the need for a modern, async web scraping solution
- Built with love and sass 💖 