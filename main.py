"""
Canvas MCP HTTP API - Vercel Serverless Function
Restructured for maintainability and comprehensive data responses.

All tools are automatically registered via the registry system.
Returns JSON responses with complete Canvas API data for better LLM context.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Import models
from api.models import ToolRequest, ToolResponse
from api.exceptions import CanvasAPIError

# Import tools (this triggers automatic registration)
from tools.base import ToolContext
from tools.registry import registry

# Explicitly import tool modules to trigger @register_tool decorators
from tools.courses import (
    list_courses,
    get_course,
    get_course_progress,
    get_course_users,
    preview_html,
)

# Initialize FastAPI app
app = FastAPI(
    title="Canvas MCP HTTP API",
    description="Student-focused Canvas LMS tools with comprehensive JSON responses",
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API Routes ====================

@app.get("/")
async def root():
    """API root - returns service information."""
    return {
        "message": "Canvas MCP HTTP API",
        "version": "2.0.0",
        "description": "Comprehensive student-focused Canvas LMS tools",
        "endpoints": {
            "/": "This page",
            "/health": "Health check",
            "/tools": "List available tools",
            "/tools/call": "Execute a tool",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tools_registered": len(registry.list_all()),
    }


@app.get("/tools")
async def list_tools():
    """
    List all available tools.

    Returns comprehensive tool metadata including:
    - Tool name
    - Description
    - Category
    """
    tools_list = []

    for tool in registry.list_all():
        tools_list.append({
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
        })

    # Group by category
    by_category = {}
    for tool_info in tools_list:
        category = tool_info["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(tool_info)

    return {
        "tools": tools_list,
        "total": len(tools_list),
        "by_category": by_category,
        "categories": list(by_category.keys()),
    }


@app.post("/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """
    Execute a specific Canvas tool.

    This is the main endpoint for tool execution. It:
    1. Validates the request
    2. Looks up the tool in the registry
    3. Creates a tool context
    4. Executes the tool
    5. Returns the result as JSON

    Args:
        request: ToolRequest with tool name, args, and Canvas credentials

    Returns:
        ToolResponse with result or error

    Example Request:
        {
            "tool": "list_courses",
            "args": {"enrollmentState": "active"},
            "canvasApiUrl": "https://canvas.example.com",
            "canvasApiToken": "your-token-here"
        }

    Example Response:
        {
            "result": {
                "courses": [
                    {
                        "id": 12345,
                        "name": "Introduction to Psychology",
                        "course_code": "PSY 101",
                        "workflow_state": "available",
                        ...  // 40+ more fields
                    }
                ],
                "total": 5
            },
            "error": null
        }
    """
    try:
        # Validate tool exists
        try:
            tool = registry.get(request.tool)
        except KeyError as e:
            available_tools = registry.list_tool_names()
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{request.tool}' not found. Available tools: {', '.join(available_tools)}",
            )

        # Create tool context
        ctx = ToolContext(
            api_url=request.canvasApiUrl,
            api_token=request.canvasApiToken,
            args=request.args,
        )

        # Execute tool
        result = await tool.run(ctx)

        # Return successful response
        return ToolResponse(result=result, error=None)

    except CanvasAPIError as e:
        # Canvas API errors (auth, not found, validation, etc.)
        return ToolResponse(
            result=None,
            error=f"Canvas API Error [{e.status_code if e.status_code else 'Unknown'}]: {e.message}",
        )

    except ValueError as e:
        # Argument validation errors
        return ToolResponse(
            result=None,
            error=f"Invalid arguments: {str(e)}",
        )

    except Exception as e:
        # Unexpected errors
        error_details = traceback.format_exc() if app.debug else str(e)
        return ToolResponse(
            result=None,
            error=f"Unexpected error: {error_details}",
        )


# ==================== Development/Debug Routes ====================

@app.get("/debug/tools/{tool_name}")
async def debug_tool(tool_name: str):
    """
    Get detailed information about a specific tool.
    Useful for debugging and development.
    """
    try:
        tool = registry.get(tool_name)
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "class": tool.__class__.__name__,
        }
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found",
        )


@app.get("/debug/registry")
async def debug_registry():
    """
    Get detailed registry information.
    Shows all tools and categories for debugging.
    """
    return {
        "total_tools": len(registry.list_all()),
        "tool_names": registry.list_tool_names(),
        "categories": registry.get_categories(),
        "tools_by_category": {
            category: [tool.name for tool in registry.list_by_category(category)]
            for category in registry.get_categories()
        },
    }
