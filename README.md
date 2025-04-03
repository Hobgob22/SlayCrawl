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

## Quick Start

1. Clone the repo:
```bash
git clone https://github.com/yourusername/slaycrawl.git
cd slaycrawl
```

2. Create a `.env` file:
```bash
REDIS_URL=redis://localhost:6379
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`. Check out the Swagger docs at `http://localhost:8000/docs`!

## API Endpoints

### Single Page Scraping

```http
POST /scrape
```

```json
{
    "url": "https://example.com",
    "render_js": false,
    "output_format": "json",
    "selectors": {
        "title": "h1",
        "content": "article p"
    }
}
```

### Site Crawling

```http
POST /crawl
```

```json
{
    "start_url": "https://example.com",
    "max_pages": 10,
    "allowed_domains": ["example.com"],
    "exclude_patterns": ["/login/*"],
    "render_js": false,
    "output_format": "json"
}
```

Check crawl status:
```http
GET /crawl/{job_id}
```

## Development

1. Create a virtual environment:
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
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -am 'Add something amazing'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Create a new Pull Request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by the need to slay web scraping with modern async Python
- Built with love and sass 💖 