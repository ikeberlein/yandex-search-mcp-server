# Yandex Search API MCP Server Dockerfile
FROM ghcr.io/astral-sh/uv:alpine

# Image metadata
LABEL org.opencontainers.image.title="Yandex Search API MCP Server"
LABEL org.opencontainers.image.description="MCP server for Yandex Search API v2 with web and AI search capabilities"
LABEL org.opencontainers.image.vendor="Yandex LLC"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app

RUN addgroup -g 1000 uv && adduser -D -u 1000 -G uv uv
RUN chown -R uv:uv /app
USER uv

# Copy dependency files
COPY pyproject.toml uv.lock .

# Install dependencies using uv
RUN uv sync --no-dev

COPY *.py .

# compile used modules
RUN uv run fastmcp version && uv run python -c "import server"

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD uv run python -c "import requests; requests.get('http://localhost:8000/health')"

# Command to run the MCP server using the virtual environment
# Use uv run fastmcp run server.py for stdio
# Or specify host and port: uv run fastmcp run --host <hostname> --port <port number> server.py
# For TCP, bind to 0.0.0.0:8000

ENTRYPOINT [ "uv", "run", "fastmcp" ]

CMD [ "run", "--no-banner", "-t", "http", "--host", "0.0.0.0", "server.py:mcp" ]

