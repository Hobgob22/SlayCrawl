# SlayCrawl

A modern, async web scraping API built with FastAPI, Redis, and Playwright. Provides powerful web scraping capabilities with JavaScript rendering support, caching, and customizable data extraction.

## Features

- 🚀 Fast async web scraping with FastAPI
- 🎭 JavaScript rendering support via Playwright with stealth mode
- 📦 Redis caching for improved performance
- 🔑 API key authentication
- 🔄 Hot reload during development
- 🎯 Health monitoring dashboard
- 📝 SQLite database for data persistence
- 🐳 Docker support with docker-compose
- 📄 HTML to Markdown conversion
- 🧹 Content cleaning (SVG removal, link text extraction)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git (optional)

### Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/Hobgob22/slaycrawl.git
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
     -d '{
       "url": "https://example.com",
       "render_js": true,
       "output_format": "markdown"
     }'
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
│   ├── formatter.py    # Content formatting utilities
│   └── worker.py       # Background task worker
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile         # Docker build instructions
├── requirements.txt   # Python dependencies
└── README.md
```

## Current Functionality

### Implemented Features
- Single page scraping with JavaScript rendering
- Stealth mode to avoid detection
- Redis caching of scraping results
- API key authentication
- Health monitoring system
- HTML to Markdown conversion
- Content cleaning (SVG removal, link extraction)
- Hot reload for development
- Docker containerization

### Planned Features
- Batch scraping of multiple URLs
- Recursive crawling with domain restrictions
- Custom CSS selectors for targeted extraction
- Background job processing
- Rate limiting
- Proxy support

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
- 🐛 [Issue Tracker](https://github.com/Hobgob22/slaycrawl/issues)
- 💬 [Discussions](https://github.com/Hobgob22/slaycrawl/discussions) 