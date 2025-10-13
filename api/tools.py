"""
FastAPI HTTP wrapper for Canvas MCP Server
Exposes MCP tools as REST API for Vercel deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
import sys

# Add src to path so we can import canvas_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from canvas_mcp.tools import (
    register_student_tools,
    register_course_tools,
    register_discussion_tools,
)
from canvas_mcp.core.client import make_canvas_request, fetch_all_paginated_results
from canvas_mcp.core.config import Config

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

# Tool registry - maps tool names to handler functions
TOOL_HANDLERS = {}

def register_tool(name: str):
    """Decorator to register tool handlers"""
    def decorator(func):
        TOOL_HANDLERS[name] = func
        return func
    return decorator

# Temporarily set Canvas config from request
def set_canvas_config(api_url: str, api_token: str):
    """Set Canvas API credentials in environment"""
    os.environ['CANVAS_API_URL'] = api_url
    os.environ['CANVAS_API_TOKEN'] = api_token

# Student Tools
@register_tool('get_my_upcoming_assignments')
async def get_my_upcoming_assignments(args: Dict[str, Any]) -> str:
    from datetime import datetime, timedelta
    from canvas_mcp.core.cache import get_course_code
    from canvas_mcp.core.dates import format_date, parse_date

    days = args.get('days', 7)
    end_date = datetime.now() + timedelta(days=days)

    events = await fetch_all_paginated_results(
        "/users/self/upcoming_events",
        params={"per_page": 100}
    )

    if isinstance(events, dict) and "error" in events:
        return f"Error fetching upcoming assignments: {events['error']}"

    if not events:
        return f"No assignments due in the next {days} days."

    # Filter to assignments only
    assignments = []
    for event in events:
        if event.get("type") == "assignment" or event.get("assignment"):
            assignment_data = event.get("assignment", event)
            due_at = assignment_data.get("due_at")

            if due_at:
                due_date = parse_date(due_at)
                if due_date and due_date <= end_date:
                    assignments.append(assignment_data)

    if not assignments:
        return f"No assignments due in the next {days} days."

    # Sort by due date
    assignments.sort(key=lambda x: parse_date(x.get("due_at", "")) or datetime.max)

    # Format output
    output_lines = [f"Upcoming Assignments (Next {days} Days):\n"]

    for assignment in assignments:
        name = assignment.get("name", "Unnamed Assignment")
        due_at = format_date(assignment.get("due_at"))
        course_id = assignment.get("course_id")

        course_display = await get_course_code(course_id) if course_id else "Unknown Course"

        submission = assignment.get("submission")
        if submission:
            submitted = submission.get("submitted_at") is not None
            status = "✅ Submitted" if submitted else "❌ Not Submitted"
        else:
            status = "❌ Not Submitted"

        output_lines.append(
            f"• {name}\n"
            f"  Course: {course_display}\n"
            f"  Due: {due_at}\n"
            f"  Status: {status}\n"
        )

    return "\n".join(output_lines)

@register_tool('get_my_course_grades')
async def get_my_course_grades(args: Dict[str, Any]) -> str:
    courses = await fetch_all_paginated_results(
        "/courses",
        params={
            "enrollment_state": "active",
            "include[]": ["total_scores", "current_grading_period_scores"],
            "per_page": 100
        }
    )

    if isinstance(courses, dict) and "error" in courses:
        return f"Error fetching courses: {courses['error']}"

    if not courses:
        return "No active course enrollments found."

    output_lines = ["Your Course Grades:\n"]

    for course in courses:
        name = course.get("name", "Unnamed Course")
        course_code = course.get("course_code", "")

        enrollments = course.get("enrollments", [])
        if enrollments:
            enrollment = enrollments[0]

            current_score = enrollment.get("computed_current_score")
            final_score = enrollment.get("computed_final_score")
            current_grade = enrollment.get("computed_current_grade", "N/A")

            if current_score is not None:
                grade_info = f"{current_grade} ({current_score:.1f}%)"
            elif final_score is not None:
                grade_info = f"{final_score:.1f}%"
            else:
                grade_info = "No grade yet"

            output_lines.append(
                f"• {course_code}: {name}\n"
                f"  Current Grade: {grade_info}\n"
            )
        else:
            output_lines.append(
                f"• {course_code}: {name}\n"
                f"  Current Grade: No enrollment data\n"
            )

    return "\n".join(output_lines)

@register_tool('get_my_courses')
async def get_my_courses(args: Dict[str, Any]) -> str:
    courses = await fetch_all_paginated_results(
        "/courses",
        params={"enrollment_state": "active", "per_page": 100}
    )

    if isinstance(courses, dict) and "error" in courses:
        return f"Error fetching courses: {courses['error']}"

    if not courses:
        return "No active courses found."

    output_lines = ["Your Active Courses:\n"]

    for course in courses:
        name = course.get("name", "Unnamed Course")
        course_code = course.get("course_code", "")
        course_id = course.get("id")

        output_lines.append(
            f"• {course_code}: {name}\n"
            f"  Course ID: {course_id}\n"
        )

    return "\n".join(output_lines)

@register_tool('get_my_todo_items')
async def get_my_todo_items(args: Dict[str, Any]) -> str:
    from canvas_mcp.core.cache import get_course_code
    from canvas_mcp.core.dates import format_date

    todos = await fetch_all_paginated_results(
        "/users/self/todo",
        params={"per_page": 100}
    )

    if isinstance(todos, dict) and "error" in todos:
        return f"Error fetching TODO items: {todos['error']}"

    if not todos:
        return "Your TODO list is empty! 🎉"

    output_lines = ["Your TODO List:\n"]

    for item in todos:
        item_type = item.get("type", "item")
        assignment = item.get("assignment", {})

        name = assignment.get("name") or item.get("title", "Unnamed item")
        due_at = format_date(assignment.get("due_at")) if assignment.get("due_at") else "No due date"
        course_id = item.get("course_id")

        course_display = await get_course_code(course_id) if course_id else "Unknown Course"

        output_lines.append(
            f"• {name}\n"
            f"  Type: {item_type.title()}\n"
            f"  Course: {course_display}\n"
            f"  Due: {due_at}\n"
        )

    return "\n".join(output_lines)

@register_tool('get_my_submission_status')
async def get_my_submission_status(args: Dict[str, Any]) -> str:
    from datetime import datetime
    from canvas_mcp.core.cache import get_course_id, get_course_code
    from canvas_mcp.core.dates import format_date, parse_date
    from canvas_mcp.core.validation import validate_params

    course_identifier = args.get('courseId')

    if course_identifier:
        course_id = await get_course_id(course_identifier)

        assignments = await fetch_all_paginated_results(
            f"/courses/{course_id}/assignments",
            params={"include[]": ["submission"], "per_page": 100}
        )

        if isinstance(assignments, dict) and "error" in assignments:
            return f"Error fetching assignments: {assignments['error']}"

        course_display = await get_course_code(course_id) or course_identifier
        output_lines = [f"Submission Status for {course_display}:\n"]
    else:
        courses = await fetch_all_paginated_results(
            "/courses",
            params={"enrollment_state": "active", "per_page": 100}
        )

        if isinstance(courses, dict) and "error" in courses:
            return f"Error fetching courses: {courses['error']}"

        output_lines = ["Submission Status (All Courses):\n"]
        all_assignments = []

        for course in courses:
            course_id = course.get("id")
            course_name = course.get("course_code", course.get("name", "Unknown"))

            assignments_data = await fetch_all_paginated_results(
                f"/courses/{course_id}/assignments",
                params={"include[]": ["submission"], "per_page": 100}
            )

            if not isinstance(assignments_data, dict) or "error" not in assignments_data:
                for assignment in assignments_data if isinstance(assignments_data, list) else []:
                    assignment["_course_name"] = course_name
                    all_assignments.append(assignment)

        assignments = all_assignments

    if not assignments:
        return "No assignments found."

    # Separate submitted and missing
    submitted = []
    missing = []

    for assignment in assignments:
        submission = assignment.get("submission")
        is_submitted = submission and submission.get("submitted_at") is not None

        if is_submitted:
            submitted.append(assignment)
        else:
            due_at = assignment.get("due_at")
            if due_at:
                due_date = parse_date(due_at)
                if due_date and due_date < datetime.now():
                    missing.append((assignment, "OVERDUE"))
                else:
                    missing.append((assignment, "NOT SUBMITTED"))
            else:
                missing.append((assignment, "NOT SUBMITTED"))

    # Format output
    if missing:
        output_lines.append(f"⚠️  Missing Submissions ({len(missing)}):\n")
        for assignment, status in missing:
            name = assignment.get("name", "Unnamed")
            due_at = format_date(assignment.get("due_at")) if assignment.get("due_at") else "No due date"
            course_name = assignment.get("_course_name", "")

            output_lines.append(
                f"• {name}\n"
                f"  {f'Course: {course_name}' if course_name else ''}\n"
                f"  Due: {due_at}\n"
                f"  Status: {status}\n"
            )

    if submitted:
        output_lines.append(f"\n✅ Submitted ({len(submitted)}):\n")
        for assignment in submitted[:10]:
            name = assignment.get("name", "Unnamed")
            submission = assignment.get("submission", {})
            submitted_at = format_date(submission.get("submitted_at"))
            course_name = assignment.get("_course_name", "")

            output_lines.append(
                f"• {name}\n"
                f"  {f'Course: {course_name}' if course_name else ''}\n"
                f"  Submitted: {submitted_at}\n"
            )

    return "\n".join(output_lines)

@register_tool('get_course_announcements')
async def get_course_announcements(args: Dict[str, Any]) -> str:
    limit = args.get('limit', 10)

    courses = await fetch_all_paginated_results(
        "/courses",
        params={"enrollment_state": "active", "per_page": 100}
    )

    if isinstance(courses, dict) and "error" in courses:
        return f"Error fetching courses: {courses['error']}"

    if not courses:
        return "No active courses found."

    all_announcements = []

    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name")

        announcements = await fetch_all_paginated_results(
            f"/courses/{course_id}/discussion_topics",
            params={"only_announcements": "true", "per_page": 100}
        )

        if isinstance(announcements, list):
            for announcement in announcements:
                announcement["_course_name"] = course_name
                all_announcements.append(announcement)

    if not all_announcements:
        return "No recent announcements found."

    # Sort by posted date
    all_announcements.sort(key=lambda x: x.get("posted_at") or "", reverse=True)

    # Take only limit
    recent_announcements = all_announcements[:limit]

    output_lines = [f"Recent Course Announcements ({len(recent_announcements)}):\n"]

    for announcement in recent_announcements:
        from canvas_mcp.core.dates import format_date

        title = announcement.get("title", "Untitled")
        message = announcement.get("message", "")
        course_name = announcement.get("_course_name", "Unknown Course")
        posted_at = format_date(announcement.get("posted_at"))

        # Truncate message
        short_message = message[:200] + "..." if len(message) > 200 else message

        output_lines.append(
            f"• {title}\n"
            f"  Course: {course_name}\n"
            f"  Posted: {posted_at}\n"
            f"  {short_message}\n"
        )

    return "\n".join(output_lines)

@register_tool('get_course_details')
async def get_course_details(args: Dict[str, Any]) -> str:
    from canvas_mcp.core.dates import format_date

    course_id = args.get('courseId')
    if not course_id:
        return "Error: courseId required"

    course = await make_canvas_request("get", f"/courses/{course_id}")

    if isinstance(course, dict) and "error" in course:
        return f"Error fetching course: {course['error']}"

    name = course.get("name", "Unnamed Course")
    course_code = course.get("course_code", "")
    start_at = format_date(course.get("start_at")) if course.get("start_at") else "Not set"
    end_at = format_date(course.get("end_at")) if course.get("end_at") else "Not set"

    output_lines = [
        "Course Details:\n",
        f"Name: {course_code} - {name}",
        f"Course ID: {course.get('id')}",
        f"Start Date: {start_at}",
        f"End Date: {end_at}",
    ]

    return "\n".join(output_lines)

@register_tool('get_course_discussions')
async def get_course_discussions(args: Dict[str, Any]) -> str:
    from canvas_mcp.core.dates import format_date

    course_id = args.get('courseId')
    limit = args.get('limit', 20)

    if not course_id:
        return "Error: courseId required"

    discussions = await fetch_all_paginated_results(
        f"/courses/{course_id}/discussion_topics",
        params={"per_page": 100}
    )

    if isinstance(discussions, dict) and "error" in discussions:
        return f"Error fetching discussions: {discussions['error']}"

    if not discussions:
        return "No discussions found for this course."

    # Sort by posted date
    discussions.sort(key=lambda x: x.get("posted_at") or "", reverse=True)

    # Take only limit
    recent_discussions = discussions[:limit]

    output_lines = [f"Course Discussions ({len(recent_discussions)}):\n"]

    for discussion in recent_discussions:
        title = discussion.get("title", "Untitled")
        message = discussion.get("message", "")
        posted_at = format_date(discussion.get("posted_at"))

        short_message = message[:200] + "..." if len(message) > 200 else message

        output_lines.append(
            f"• {title}\n"
            f"  Posted: {posted_at}\n"
            f"  {short_message}\n"
        )

    return "\n".join(output_lines)

@app.get("/")
async def root():
    return {"message": "Canvas MCP HTTP API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": list(TOOL_HANDLERS.keys())
    }

@app.post("/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """Call a specific Canvas tool"""

    # Set Canvas credentials in environment
    set_canvas_config(request.canvasApiUrl, request.canvasApiToken)

    # Get tool handler
    if request.tool not in TOOL_HANDLERS:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool}")

    handler = TOOL_HANDLERS[request.tool]

    try:
        result = await handler(request.args)
        return ToolResponse(result=result)
    except Exception as e:
        return ToolResponse(result="", error=str(e))
