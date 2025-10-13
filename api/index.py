"""
Vercel serverless function entry point
Simple proxy - just returns API info for now since full canvas_mcp needs restructuring
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
import httpx
import os

app = FastAPI(title="Canvas MCP HTTP API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    tool: str
    args: Dict[str, Any] = {}
    canvasApiUrl: str
    canvasApiToken: str

class ToolResponse(BaseModel):
    result: str
    error: Optional[str] = None

# Canvas API helper
async def call_canvas_api(api_url: str, token: str, endpoint: str) -> Any:
    """Make Canvas API request"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url}/api/v1{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            params={"per_page": 100}
        )
        response.raise_for_status()
        return response.json()

# Simple tool handlers
async def get_my_courses(api_url: str, token: str) -> str:
    """Get active courses"""
    courses = await call_canvas_api(api_url, token, "/courses?enrollment_state=active")

    if not courses:
        return "No active courses found."

    output = "Your Active Courses:\n\n"
    for course in courses:
        name = course.get("name", "Unnamed")
        code = course.get("course_code", "")
        output += f"• {code}: {name}\n  Course ID: {course.get('id')}\n\n"

    return output

async def get_my_course_grades(api_url: str, token: str) -> str:
    """Get course grades"""
    courses = await call_canvas_api(
        api_url, token,
        "/courses?enrollment_state=active&include[]=total_scores"
    )

    if not courses:
        return "No active courses found."

    output = "Your Course Grades:\n\n"
    for course in courses:
        name = course.get("name", "Unnamed")
        code = course.get("course_code", "")
        enrollments = course.get("enrollments", [])

        if enrollments:
            enrollment = enrollments[0]
            score = enrollment.get("computed_current_score")
            grade = enrollment.get("computed_current_grade", "N/A")
            grade_info = f"{grade} ({score:.1f}%)" if score else "No grade yet"
        else:
            grade_info = "No enrollment data"

        output += f"• {code}: {name}\n  Grade: {grade_info}\n\n"

    return output

async def get_my_todo_items(api_url: str, token: str) -> str:
    """Get TODO items"""
    todos = await call_canvas_api(api_url, token, "/users/self/todo")

    if not todos:
        return "Your TODO list is empty! 🎉"

    output = "Your TODO List:\n\n"
    for item in todos:
        assignment = item.get("assignment", {})
        name = assignment.get("name") or item.get("title", "Unnamed")
        item_type = item.get("type", "item")
        output += f"• {name}\n  Type: {item_type}\n\n"

    return output

@app.get("/")
async def root():
    return {"message": "Canvas MCP HTTP API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            "get_my_courses",
            "get_my_course_grades",
            "get_my_todo_items"
        ]
    }

@app.post("/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """Call a Canvas tool"""

    try:
        if request.tool == "get_my_courses":
            result = await get_my_courses(request.canvasApiUrl, request.canvasApiToken)
        elif request.tool == "get_my_course_grades":
            result = await get_my_course_grades(request.canvasApiUrl, request.canvasApiToken)
        elif request.tool == "get_my_todo_items":
            result = await get_my_todo_items(request.canvasApiUrl, request.canvasApiToken)
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool}")

        return ToolResponse(result=result)
    except Exception as e:
        return ToolResponse(result="", error=str(e))
