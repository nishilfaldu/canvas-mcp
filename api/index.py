"""
Canvas MCP HTTP API - Vercel Serverless Function
Exposes all student + shared Canvas LMS tools via REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import httpx

app = FastAPI(title="Canvas MCP HTTP API")

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

# Tool Handlers
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

async def get_my_upcoming_assignments(api_url: str, token: str, days: int = 7) -> str:
    """Get upcoming assignments"""
    events = await call_canvas_api(api_url, token, "/users/self/upcoming_events")

    if not events:
        return f"No assignments due in the next {days} days."

    end_date = datetime.now() + timedelta(days=days)
    assignments = []

    for event in events:
        if event.get("type") == "assignment" or event.get("assignment"):
            assignment_data = event.get("assignment", event)
            due_at = assignment_data.get("due_at")

            if due_at:
                try:
                    due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                    if due_date <= end_date:
                        assignments.append(assignment_data)
                except:
                    continue

    if not assignments:
        return f"No assignments due in the next {days} days."

    assignments.sort(key=lambda x: x.get("due_at", ""))

    output = f"Upcoming Assignments (Next {days} Days):\n\n"
    for assignment in assignments:
        name = assignment.get("name", "Unnamed Assignment")
        due_at = assignment.get("due_at", "Unknown")
        course_id = assignment.get("course_id")

        submission = assignment.get("submission")
        status = "✅ Submitted" if submission and submission.get("submitted_at") else "❌ Not Submitted"

        output += f"• {name}\n  Course ID: {course_id}\n  Due: {due_at}\n  Status: {status}\n\n"

    return output

async def get_course_announcements(api_url: str, token: str, limit: int = 10) -> str:
    """Get recent announcements from all courses"""
    courses = await call_canvas_api(api_url, token, "/courses?enrollment_state=active")

    if not courses:
        return "No active courses found."

    all_announcements = []

    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name")

        try:
            announcements = await call_canvas_api(
                api_url, token,
                f"/courses/{course_id}/discussion_topics?only_announcements=true"
            )

            for announcement in announcements:
                announcement["_course_name"] = course_name
                all_announcements.append(announcement)
        except:
            continue

    if not all_announcements:
        return "No recent announcements found."

    all_announcements.sort(key=lambda x: x.get("posted_at", ""), reverse=True)

    recent = all_announcements[:limit]

    output = f"Recent Course Announcements ({len(recent)}):\n\n"
    for announcement in recent:
        title = announcement.get("title", "Untitled")
        course_name = announcement.get("_course_name", "Unknown Course")
        posted_at = announcement.get("posted_at", "Unknown")
        message = announcement.get("message", "")

        short_message = message[:200] + "..." if len(message) > 200 else message

        output += f"• {title}\n  Course: {course_name}\n  Posted: {posted_at}\n  {short_message}\n\n"

    return output

async def get_course_discussions(api_url: str, token: str, course_id: int, limit: int = 20) -> str:
    """Get discussion topics from a course"""
    discussions = await call_canvas_api(api_url, token, f"/courses/{course_id}/discussion_topics")

    if not discussions:
        return "No discussions found for this course."

    discussions.sort(key=lambda x: x.get("posted_at", ""), reverse=True)

    recent = discussions[:limit]

    output = f"Course Discussions ({len(recent)}):\n\n"
    for discussion in recent:
        title = discussion.get("title", "Untitled")
        posted_at = discussion.get("posted_at", "Unknown")
        message = discussion.get("message", "")

        short_message = message[:200] + "..." if len(message) > 200 else message

        output += f"• {title}\n  Posted: {posted_at}\n  {short_message}\n\n"

    return output

async def get_course_details(api_url: str, token: str, course_id: int) -> str:
    """Get detailed course information"""
    course = await call_canvas_api(api_url, token, f"/courses/{course_id}")

    name = course.get("name", "Unnamed Course")
    code = course.get("course_code", "")
    start_at = course.get("start_at", "Not set")
    end_at = course.get("end_at", "Not set")

    output = "Course Details:\n\n"
    output += f"Name: {code} - {name}\n"
    output += f"Course ID: {course.get('id')}\n"
    output += f"Start Date: {start_at}\n"
    output += f"End Date: {end_at}\n"

    return output

async def get_my_submission_status(api_url: str, token: str, course_id: Optional[int] = None) -> str:
    """Get submission status for assignments"""
    if course_id:
        assignments = await call_canvas_api(
            api_url, token,
            f"/courses/{course_id}/assignments?include[]=submission"
        )
        assignments = [assignments] if isinstance(assignments, dict) else assignments
    else:
        courses = await call_canvas_api(api_url, token, "/courses?enrollment_state=active")
        all_assignments = []

        for course in courses:
            cid = course.get("id")
            try:
                course_assignments = await call_canvas_api(
                    api_url, token,
                    f"/courses/{cid}/assignments?include[]=submission"
                )
                for assignment in course_assignments:
                    assignment["_course_name"] = course.get("name", "")
                    all_assignments.append(assignment)
            except:
                continue

        assignments = all_assignments

    if not assignments:
        return "No assignments found."

    submitted = []
    missing = []

    for assignment in assignments:
        submission = assignment.get("submission")
        is_submitted = submission and submission.get("submitted_at")

        if is_submitted:
            submitted.append(assignment)
        else:
            due_at = assignment.get("due_at")
            if due_at:
                try:
                    due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
                    assignment["_is_overdue"] = due_date < datetime.now()
                except:
                    pass
            missing.append(assignment)

    output = "Submission Status:\n\n"

    if missing:
        output += f"⚠️  Missing Submissions ({len(missing)}):\n\n"
        for assignment in missing:
            name = assignment.get("name", "Unnamed")
            due_at = assignment.get("due_at", "No due date")
            course_name = assignment.get("_course_name", "")
            status = "OVERDUE" if assignment.get("_is_overdue") else "NOT SUBMITTED"

            output += f"• {name}\n"
            if course_name:
                output += f"  Course: {course_name}\n"
            output += f"  Due: {due_at}\n"
            output += f"  Status: {status}\n\n"

    if submitted:
        output += f"✅ Submitted ({len(submitted)}):\n\n"
        for assignment in submitted[:10]:
            name = assignment.get("name", "Unnamed")
            submission = assignment.get("submission", {})
            submitted_at = submission.get("submitted_at", "Unknown")
            course_name = assignment.get("_course_name", "")

            output += f"• {name}\n"
            if course_name:
                output += f"  Course: {course_name}\n"
            output += f"  Submitted: {submitted_at}\n\n"

    return output

# API Routes
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
        "tools": [
            "get_my_courses",
            "get_my_course_grades",
            "get_my_todo_items",
            "get_my_upcoming_assignments",
            "get_course_announcements",
            "get_course_discussions",
            "get_course_details",
            "get_my_submission_status"
        ]
    }

@app.post("/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """Call a specific Canvas tool"""

    try:
        if request.tool == "get_my_courses":
            result = await get_my_courses(request.canvasApiUrl, request.canvasApiToken)
        elif request.tool == "get_my_course_grades":
            result = await get_my_course_grades(request.canvasApiUrl, request.canvasApiToken)
        elif request.tool == "get_my_todo_items":
            result = await get_my_todo_items(request.canvasApiUrl, request.canvasApiToken)
        elif request.tool == "get_my_upcoming_assignments":
            days = request.args.get("days", 7)
            result = await get_my_upcoming_assignments(request.canvasApiUrl, request.canvasApiToken, days)
        elif request.tool == "get_course_announcements":
            limit = request.args.get("limit", 10)
            result = await get_course_announcements(request.canvasApiUrl, request.canvasApiToken, limit)
        elif request.tool == "get_course_discussions":
            course_id = request.args.get("courseId")
            limit = request.args.get("limit", 20)
            if not course_id:
                raise HTTPException(status_code=400, detail="courseId required")
            result = await get_course_discussions(request.canvasApiUrl, request.canvasApiToken, course_id, limit)
        elif request.tool == "get_course_details":
            course_id = request.args.get("courseId")
            if not course_id:
                raise HTTPException(status_code=400, detail="courseId required")
            result = await get_course_details(request.canvasApiUrl, request.canvasApiToken, course_id)
        elif request.tool == "get_my_submission_status":
            course_id = request.args.get("courseId")
            result = await get_my_submission_status(request.canvasApiUrl, request.canvasApiToken, course_id)
        else:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool}")

        return ToolResponse(result=result)
    except Exception as e:
        return ToolResponse(result="", error=str(e))
