# Yandex Search API MCP Server

A FastMCP-based microservice that provides Yandex Search API v2 capabilities via two MCP tools:
- `web_search` – uses the web search endpoint and returns XML.

## Quick Start

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run the server locally
uv run fastmcp run server.py
# Or specify a custom host and port:
# uv run fastmcp run --host 0.0.0.0 --port 8000 server.py
```

Ensure the following environment variables are set:
- `SEARCH_API_KEY` – your Yandex Search API key.

## Docker

```bash
docker build -t yandex-mcp-server-image:latest .
docker run -e SEARCH_API_KEY=<your_api_key> yandex-mcp-server-image:latest
```

## API Endpoints

- `ai_search` – accepts a JSON payload with `query` and `search_region`.
- `web_search` – accepts a JSON payload with `query` and `search_region` and returns XML.

## Development

- **Run the server** with `uv run fastmcp run server.py`.
- **Add new tools** by following the pattern in `server.py`: register a `@mcp.tool()`, validate input with `validate_input_data`, and call a helper in `detail.py`.
- **Improve XML parsing** by switching from regexes to `xml.etree.ElementTree` if the schema changes.

## License

Apache‑2.0
