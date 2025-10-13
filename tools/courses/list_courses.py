"""
List Courses Tool

Lists all courses for the current user with comprehensive data.
Returns full JSON responses with all available Canvas course fields.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils import build_course_params, COURSE_INCLUDE_ALL


@register_tool
class ListCoursesTool(BaseTool):
    """
    List all courses for the current user.

    Returns comprehensive course data including:
    - Basic info (name, code, dates)
    - Syllabus content
    - Enrollment/grade information
    - Course progress
    - Permissions
    - Sections
    - Term information
    """

    name = "list_courses"
    description = (
        "List all courses for the current user with comprehensive data. "
        "Includes syllabus, grades, progress, permissions, and more. "
        "Perfect for answering 'What courses am I taking?' or 'Show me my courses with grades.'"
    )
    category = "courses"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        # Optional filters
        if "enrollmentState" in args:
            valid_states = ["active", "invited_or_pending", "completed", "all"]
            if args["enrollmentState"] not in valid_states:
                raise ValueError(
                    f"enrollmentState must be one of: {', '.join(valid_states)}"
                )

        if "state" in args:
            if not isinstance(args["state"], list):
                raise ValueError("state must be a list")

        if "perPage" in args:
            per_page = args["perPage"]
            if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
                raise ValueError("perPage must be an integer between 1 and 100")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the list_courses tool.

        Args:
            ctx: Tool execution context

        Supported args:
            - enrollmentState (str): Filter by enrollment state ("active", "invited_or_pending", "completed")
            - state (list[str]): Filter by course state (["available"], ["completed"])
            - homeroom (bool): Return only homeroom courses
            - includeSyllabus (bool): Include full syllabus HTML (default: True)
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "courses": [<Course objects>],
                "total": <int>
            }
        """
        # Extract arguments with defaults
        enrollment_state = ctx.args.get("enrollmentState", "active")
        state = ctx.args.get("state")
        homeroom = ctx.args.get("homeroom")
        include_syllabus = ctx.args.get("includeSyllabus", True)
        per_page = ctx.args.get("perPage", 100)

        # Build include parameters for comprehensive data
        include_params = COURSE_INCLUDE_ALL.copy()

        # Optionally exclude syllabus if not needed (it can be large)
        if not include_syllabus and "syllabus_body" in include_params:
            include_params.remove("syllabus_body")

        # Build query parameters
        params = build_course_params(
            include=include_params,
            enrollment_state=enrollment_state,
            state=state,
            homeroom=homeroom,
            per_page=per_page,
        )

        # Fetch courses with pagination
        courses = await ctx.client.get(
            "/courses",
            params=params,
            paginate=True,  # Automatically fetch all pages
        )

        # Return comprehensive response
        return {
            "courses": courses,
            "total": len(courses),
            "filters": {
                "enrollmentState": enrollment_state,
                "state": state,
                "homeroom": homeroom,
            },
        }
