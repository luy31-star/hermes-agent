#!/usr/bin/env python3
"""
Knowledge Vault Search Tool

Provides access to the desktop knowledge vault for searching notes and retrieving content.
Only available when running in desktop mode with DESKTOP_BRIDGE_URL configured.
"""

import os
import requests
from typing import Dict, Any, List, Optional
from tools.registry import registry, tool_error


def tool_success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper to return a successful tool result."""
    result = {"success": True, "message": message}
    if data:
        result.update(data)
    return result


def check_knowledge_vault_available() -> bool:
    """Check if knowledge vault is available (desktop mode with bridge URL)."""
    return bool(os.getenv("DESKTOP_BRIDGE_URL", "").strip())


def _handle_knowledge_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search the desktop knowledge vault for relevant notes.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        List of matching notes with titles, excerpts, and IDs
    """
    query = args.get("query", "").strip()
    if not query:
        return tool_error("Search query is required")
    
    limit = args.get("limit", 5)
    if not isinstance(limit, int) or limit < 1 or limit > 20:
        limit = 5
    
    # Get desktop bridge URL from environment
    bridge_url = os.getenv("DESKTOP_BRIDGE_URL", "").strip()
    if not bridge_url:
        return tool_error(
            "Knowledge vault is not available. This feature requires desktop mode."
        )
    
    try:
        # Call desktop bridge knowledge search API
        response = requests.get(
            f"{bridge_url}/knowledge/search",
            params={"q": query, "limit": limit},
            timeout=10
        )
        response.raise_for_status()
        results = response.json()
        
        if not results:
            return tool_success(
                f"No notes found matching '{query}'.",
                {"query": query, "results": []}
            )
        
        # Format results for LLM
        formatted_results = []
        for item in results:
            formatted_results.append({
                "id": item.get("id"),
                "title": item.get("title", "Untitled"),
                "excerpt": item.get("excerpt", ""),
                "tags": item.get("tags", []),
                "updated_at": item.get("updated_at"),
            })
        
        summary = f"Found {len(formatted_results)} note(s) matching '{query}':\n\n"
        for idx, note in enumerate(formatted_results, 1):
            summary += f"{idx}. **{note['title']}**\n"
            if note['excerpt']:
                summary += f"   {note['excerpt'][:200]}...\n"
            if note['tags']:
                summary += f"   Tags: {', '.join(note['tags'])}\n"
            summary += "\n"
        
        summary += "\nUse `knowledge_get_note` with the note ID to retrieve full content."
        
        return tool_success(summary, {"query": query, "results": formatted_results})
    
    except requests.exceptions.Timeout:
        return tool_error("Knowledge search timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        return tool_error(f"Failed to search knowledge vault: {str(e)}")
    except Exception as e:
        return tool_error(f"Unexpected error during knowledge search: {str(e)}")


def _handle_knowledge_get_note(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve full content of a specific note from the knowledge vault.
    
    Args:
        note_id: The ID of the note to retrieve
    
    Returns:
        Full note content including title, body, tags, and metadata
    """
    note_id = args.get("note_id", "").strip()
    if not note_id:
        return tool_error("Note ID is required")
    
    bridge_url = os.getenv("DESKTOP_BRIDGE_URL", "").strip()
    if not bridge_url:
        return tool_error(
            "Knowledge vault is not available. This feature requires desktop mode."
        )
    
    try:
        response = requests.get(
            f"{bridge_url}/knowledge/notes/{note_id}",
            timeout=10
        )
        response.raise_for_status()
        note = response.json()
        
        # Format note content for LLM
        content = f"# {note.get('title', 'Untitled')}\n\n"
        
        if note.get('tags'):
            content += f"**Tags:** {', '.join(note['tags'])}\n\n"
        
        if note.get('updated_at'):
            content += f"**Last updated:** {note['updated_at']}\n\n"
        
        content += "---\n\n"
        content += note.get('content', '')
        
        return tool_success(content, {"note_id": note_id, "note": note})
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return tool_error(f"Note with ID '{note_id}' not found")
        return tool_error(f"Failed to retrieve note: {str(e)}")
    except requests.exceptions.Timeout:
        return tool_error("Request timed out. Please try again.")
    except Exception as e:
        return tool_error(f"Unexpected error retrieving note: {str(e)}")


# Tool schemas
KNOWLEDGE_SEARCH_SCHEMA = {
    "name": "knowledge_search",
    "description": (
        "Search the desktop knowledge vault for relevant notes and information. "
        "Returns matching notes with titles, excerpts, and IDs. "
        "Only available in desktop mode."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to find relevant notes",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (1-20, default: 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}

KNOWLEDGE_GET_NOTE_SCHEMA = {
    "name": "knowledge_get_note",
    "description": (
        "Retrieve the full content of a specific note from the knowledge vault. "
        "Use this after knowledge_search to get complete note details. "
        "Only available in desktop mode."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "note_id": {
                "type": "string",
                "description": "The ID of the note to retrieve (from knowledge_search results)",
            },
        },
        "required": ["note_id"],
    },
}

# Register tools
registry.register(
    name="knowledge_search",
    toolset="knowledge_vault",
    schema=KNOWLEDGE_SEARCH_SCHEMA,
    handler=lambda args, **kw: _handle_knowledge_search(args),
    check_fn=check_knowledge_vault_available,
    requires_env=[],
    is_async=False,
    emoji="📚",
)

registry.register(
    name="knowledge_get_note",
    toolset="knowledge_vault",
    schema=KNOWLEDGE_GET_NOTE_SCHEMA,
    handler=lambda args, **kw: _handle_knowledge_get_note(args),
    check_fn=check_knowledge_vault_available,
    requires_env=[],
    is_async=False,
    emoji="📄",
)

