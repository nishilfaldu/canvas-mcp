"""
Get Course Tool

Fetches detailed information about a specific course.
Returns comprehensive course data with all available fields.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_single_course_params, COURSE_INCLUDE_ALL


@register_tool
class GetCourseTool(BaseTool):
    """
    Get detailed information about a specific course.

    Returns comprehensive course data including:
    - Complete course metadata
    - Full syllabus HTML
    - Enrollment and grade information
    - Course progress
    - Permissions
    - Term details
    - All course settings
    """

    name = "get_course"
    description = (
        "Get detailed information about a specific course by ID. "
        "Returns comprehensive data including syllabus, grades, progress, permissions, and settings. "
        "Use this when student asks about a specific course."
    )
    category = "courses"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the get_course tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID

        Optional args:
            - includeSyllabus (bool): Include full syllabus HTML (default: True)
            - teacherLimit (int): Maximum number of teachers to include (default: None)

        Returns:
            {
                "course": <Course object with all fields>
            }
        """
        course_id = ctx.args["courseId"]
        include_syllabus = ctx.args.get("includeSyllabus", True)
        teacher_limit = ctx.args.get("teacherLimit")

        # Build include parameters for comprehensive data
        include_params = COURSE_INCLUDE_ALL.copy()

        # Optionally exclude syllabus if not needed
        if not include_syllabus and "syllabus_body" in include_params:
            include_params.remove("syllabus_body")

        # Build query parameters
        params = build_single_course_params(
            include=include_params,
            teacher_limit=teacher_limit,
        )

        # Fetch course details
        course = await ctx.client.get(
            f"/courses/{course_id}",
            params=params,
        )

        return {
            "course": course,
        }
