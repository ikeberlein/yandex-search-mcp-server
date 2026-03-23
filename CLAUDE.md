# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Install dependencies**:
  ```bash
  python3 -m pip install -r requirements.txt
  ```
- **Run the server (local)**:
  ```bash
  # Ensure SEARCH_API_KEY environment variable is set
  uv run fastmcp run server.py
  # Or with host and port:
  # uv run fastmcp run --host <hostname> --port <port number> server.py
  ```
- **Docker**:
  - Build container:
    ```bash
    docker build -t yandex-mcp-server-image:latest .
    ```
  - Run container (replace placeholders):
    ```bash
    docker run -e SEARCH_API_KEY=<your_api_key> -e FOLDER_ID=<your_folder_id> yandex-mcp-server-image:latest
    ```
- **Testing**: Currently no automated test suite. Use manual testing via the MCP client or add tests under `tests/`.
- **Linting**: No lint configuration present. You can add a tool like `ruff` or `flake8` by installing and creating a config file.

## Architecture Overview

The server is built with **FastMCP** and consists of two main layers:

1. **API Layer (`server.py`)**:
   - Registers one MCP tool: `web_search`.
   - Performs input validation (required `query` and `search_region`).
   - Maps region to Yandex Search API parameters (e.g., Turkish vs. English).
   - Handles error cases and returns JSON‑formatted responses.
   - Includes helper functions for XML parsing and text cleaning.

2. **Low‑level HTTP & Business Logic (`detail.py`)**:
   - Contains reusable HTTP request logic (`make_http_request`).
   - Handles authentication via `SEARCH_API_KEY` and `FOLDER_ID` environment variables.
   - Provides two concrete callers:
      * `call_web_search` – uses the web search endpoint and returns XML.
   - Includes XML extraction utilities (`extract_documents_from_xml`, `process_single_document`) that turn raw XML into clean response data.

**Key implementation choices**:
- **Region‑aware configuration**: The server automatically selects `SEARCH_TYPE_TR` for Turkish queries and `SEARCH_TYPE_COM` for English, keeping the API surface simple.
- **Error handling**: Validation is done early (`validate_input_data`) to return clear error messages before making network calls.
- **XML‑centric web search**: The web endpoint returns XML; the code uses simple regexes to extract `url`, `headline`, `title`, and `passage` elements. This avoids a heavy XML parser because the data volume is small and the format is predictable.
- **Environment‑driven secrets**: No secret values are hard‑coded; they are injected via environment variables, aligning with the Docker and MCP‑remote deployment patterns.

## How to Extend

- **Add new tools**: Follow the pattern in `server.py` – register a `@mcp.tool()` function, validate its input with `validate_input_data`, and call a helper in `detail.py`.
- **Improve XML parsing**: If the XML schema changes, consider using `xml.etree.ElementTree` for robustness.
- **Testing**: Create a `tests/` directory with `pytest` files that mock `make_http_request` to avoid real network calls.
