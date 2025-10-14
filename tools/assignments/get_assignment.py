"""
Get Assignment Tool

Fetches detailed information about a specific assignment.
Returns comprehensive assignment data with submission and scoring info.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_single_assignment_params, ASSIGNMENT_INCLUDE_ALL


@register_tool
class GetAssignmentTool(BaseTool):
    """
    Get detailed information about a specific assignment.

    Returns comprehensive assignment data including:
    - Complete assignment details
    - Submission requirements and status
    - Rubric and grading information
    - Score statistics
    - Due dates (with overrides applied)
    """

    name = "get_assignment"
    description = (
        "Get detailed information about a specific assignment by ID. "
        "Returns comprehensive data including submission status, rubric, scores, and requirements. "
        "Use when student asks 'Tell me about this assignment' or 'What do I need to do for assignment X?'"
    )
    category = "assignments"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

        if "assignmentId" not in args:
            raise ValueError("assignmentId is required")

        assignment_id = args["assignmentId"]
        if not isinstance(assignment_id, int) or assignment_id <= 0:
            raise ValueError("assignmentId must be a positive integer")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the get_assignment tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID
            - assignmentId (int): Canvas assignment ID

        Returns:
            {
                "courseId": <int>,
                "assignmentId": <int>,
                "assignment": <Assignment object with all fields>
            }
        """
        course_id = ctx.args["courseId"]
        assignment_id = ctx.args["assignmentId"]

        # Build include parameters for comprehensive data
        include_params = ASSIGNMENT_INCLUDE_ALL.copy()

        # Build query parameters
        params = build_single_assignment_params(
            include=include_params,
            override_assignment_dates=True,  # Apply overrides for accurate dates
            all_dates=True,  # Include all date variants
        )

        # Fetch assignment details
        assignment = await ctx.client.get(
            f"/courses/{course_id}/assignments/{assignment_id}",
            params=params,
        )

        return {
            "courseId": course_id,
            "assignmentId": assignment_id,
            "assignment": assignment,
        }
