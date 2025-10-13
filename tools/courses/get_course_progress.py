"""
Get Course Progress Tool

Fetches the student's progress in a specific course.
Shows module/requirement completion tracking.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool


@register_tool
class GetCourseProgressTool(BaseTool):
    """
    Get student's progress in a specific course.

    Returns progress information including:
    - Total requirements
    - Completed requirements
    - Next requirement URL
    - Completion date (if completed)
    """

    name = "get_course_progress"
    description = (
        "Get the student's progress tracking for a specific course. "
        "Shows how many requirements are completed, what's next, and completion status. "
        "Use when student asks 'How am I doing in this course?' or 'What's my progress?'"
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
        Execute the get_course_progress tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID

        Returns:
            {
                "courseId": <int>,
                "progress": {
                    "requirement_count": <int>,
                    "requirement_completed_count": <int>,
                    "next_requirement_url": <str | null>,
                    "completed_at": <datetime | null>
                },
                "completion_percentage": <float>
            }
        """
        course_id = ctx.args["courseId"]

        # Fetch progress for current user
        # Canvas uses "self" to refer to the authenticated user
        progress = await ctx.client.get(
            f"/courses/{course_id}/users/self/progress"
        )

        # Calculate completion percentage
        requirement_count = progress.get("requirement_count", 0)
        completed_count = progress.get("requirement_completed_count", 0)

        completion_percentage = 0.0
        if requirement_count > 0:
            completion_percentage = (completed_count / requirement_count) * 100

        return {
            "courseId": course_id,
            "progress": progress,
            "completionPercentage": round(completion_percentage, 2),
        }
