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

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SlayCrawl.git
cd SlayCrawl
```

2. Start the application using Docker Compose:
```bash
docker-compose up -d
```

The application will automatically:
- Create the necessary data directory
- Initialize the SQLite database with required tables
- Set up Redis for caching
- Start the web server

3. Access the web interface:
- Main UI: http://localhost:8000
- Health Check UI: http://localhost:8000/health-ui
- API Documentation: http://localhost:8000/docs

Note: The database (scraper.db) is automatically created on first startup. It's stored in the `data` directory and persists between container restarts. This file is not included in the Git repository for security reasons.

## Web UI Access

The web interface is freely accessible without any API key requirements. You can use all the features through the web UI without authentication.

## API Access

When using SlayCrawl in your applications or making direct API calls, you'll need to use an API key.

### Default Admin API Key

On first startup, SlayCrawl automatically creates a default admin API key. You can find this key in `config/admin_key.txt`. This key has full administrative access and can be used to:

- Create additional API keys
- List all API keys
- Delete API keys
- Access all scraping features

### Using the API

To use the API in your applications, include the API key in the `X-API-Key` header:

```python
import requests

headers = {
    'X-API-Key': 'your-api-key'
}

response = requests.post('http://localhost:8000/scrape', 
    headers=headers,
    json={
        'url': 'https://example.com',
        'render_js': True
    }
)
```

### Creating Additional API Keys

You can create additional API keys using the admin key:

```python
import requests

headers = {
    'X-API-Key': 'your-admin-key'
}

response = requests.post('http://localhost:8000/api/keys',
    headers=headers,
    json={
        'name': 'My API Key',
        'description': 'Key for my application',
        'role': 'user'
    }
)
```

## Security Notes

1. The default admin key is intended for initial setup and development
2. For production use, it's recommended to:
   - Create new API keys for each application
   - Keep the admin key secure
   - Use user-level API keys for regular operations

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: SQLite database location (default: sqlite+aiosqlite:///scraper.db)
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379)
- `LOG_LEVEL`: Logging level (default: INFO)

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