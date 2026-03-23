"""
Yandex Search API MCP Server

This module implements an MCP server providing access to Yandex Search API v2 features:
- Web search (preferred endpoint)

Copyright © 2025 Yandex LLC. Licensed under Apache License 2.0.

Features:
- FastMCP integration
- Input validation
- Error handling
- Configuration via environment variables
"""

import json
import os
import re
from starlette.responses import JSONResponse
from typing import Dict, Any

from fastmcp import FastMCP
from detail import validate_input_data, call_web_search

# Create an MCP server
mcp = FastMCP(name="Yandex Search Api v2")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})


def extract_documents_from_xml(xml_content):
    """Извлекает отдельные документы из XML контента"""
    doc_strings = []
    lines = xml_content.split('\n')
    current_doc = []
    in_doc = False

    for line in lines:
        if '<doc ' in line and 'id=' in line:
            in_doc = True
            current_doc = [line]
        elif in_doc and '</doc>' in line:
            current_doc.append(line)
            doc_strings.append('\n'.join(current_doc))
            in_doc = False
        elif in_doc:
            current_doc.append(line)

    return doc_strings


def clean_text(text):
    """Очищает текст от hlword тегов"""
    if not text:
        return ""
    cleaned = re.sub(r'<hlword>|</hlword>', '', text)
    return cleaned.strip()


def extract_document_elements(doc_string):
    """Извлекает элементы из строки документа"""
    url_match = re.search(r'<url>(.*?)</url>', doc_string)
    headline_match = re.search(r'<headline>(.*?)</headline>', doc_string)
    title_match = re.search(r'<title>(.*?)</title>', doc_string)
    passage_matches = re.findall(r'<passage>(.*?)</passage>', doc_string)
    extended_text_match = re.search(r'<extended-text>(.*?)</extended-text>', doc_string)

    return {
        'url': url_match.group(1) if url_match else None,
        'headline': headline_match.group(1) if headline_match else None,
        'title': title_match.group(1) if title_match else None,
        'passages': passage_matches,
        'extended_text': extended_text_match.group(1) if extended_text_match else None
    }


def get_best_content(elements):
    """Выбирает лучший контент из доступных элементов"""
    if elements['headline']:
        return clean_text(elements['headline']), "headline"
    elif elements['title']:
        return clean_text(elements['title']), "title"
    elif elements['passages']:
        cleaned_passages = [clean_text(p) for p in elements['passages'] if p]
        return " ".join(cleaned_passages), "passages"
    elif elements['extended_text']:
        return clean_text(elements['extended_text']), "extended-text"
    else:
        return None, None


def process_single_document(doc_string):
    """Обрабатывает один документ и возвращает результат"""
    elements = extract_document_elements(doc_string)

    if not elements['url']:
        return None

    content, source = get_best_content(elements)

    if content:
        return {
            'data': content,
            'source': elements['url']
        }

    return None


def xweb_search(body: dict) -> str:
    """
    Use this tool when the user needs to search online.

    Args:
        body (dict): Required. input containing:
            - query: Required. Search query string. Can contain a question and keywords
            - search_region: Required. Search region. Valid values: 'ru' - Russian region, 'en' - English region
            - count: Optional, default 4. Maximum results to return.

        minimal example: "body": {
                             "query": "who won the latest F1 race 2025",
                             "search_region": "ru"
                         }

    Returns:
        dict: array of data and source
    """
    data = body
    required_keys = {"query", "search_region"}
    if error_message := validate_input_data(data, required_keys):
        return error_message

    decoded_data = call_web_search(data)
    doc_strings = extract_documents_from_xml(decoded_data)
    response = []

    for doc_string in doc_strings:
        doc_result = process_single_document(doc_string)
        if doc_result:
            response.append(doc_result)

    return json.dumps(response, ensure_ascii=False, indent=2)

@mcp.tool()
def web_search(body: dict) -> str:
    """
    This is "Web Search" tool.  Use it to search information online in the Web/Internet.

    Args:
        body (dict): Required. input containing:
            - query: Required. Search query string. Can contain a question and keywords
            - search_region: Required. Search region. Valid values: 'ru' - Russian region, 'en' - English region
            - count: Optional, default 4. Maximum results to return.

        minimal example: "body": {
                             "query": "who won the latest F1 race 2025",
                             "search_region": "ru"
                         }

    Returns:
        dict: array of data and source
    """
    data = body
    required_keys = {"query", "search_region"}
    if error_message := validate_input_data(data, required_keys):
        return error_message

    decoded_data = call_web_search(data)
    doc_strings = extract_documents_from_xml(decoded_data)
    response = []

    for doc_string in doc_strings:
        doc_result = process_single_document(doc_string)
        if doc_result:
            response.append(doc_result)

    return json.dumps(response, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    try:
        mcp.run()
    except Exception as e:
        raise

