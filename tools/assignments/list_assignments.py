"""
List Assignments Tool

Lists all assignments for a specific course with comprehensive data.
Returns full JSON responses with submission status, scores, and due dates.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_assignment_params, ASSIGNMENT_INCLUDE_ALL


@register_tool
class ListAssignmentsTool(BaseTool):
    """
    List all assignments for a specific course.

    Returns comprehensive assignment data including:
    - Assignment details (name, description, points)
    - Due dates and lock dates
    - Student's submission status
    - Score statistics
    - Assignment overrides
    """

    name = "list_assignments"
    description = (
        "List all assignments for a specific course with comprehensive data. "
        "Includes submission status, scores, due dates, and requirements. "
        "Use when student asks 'What assignments do I have?' or 'Show my upcoming assignments for this course.'"
    )
    category = "assignments"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

        # Validate bucket filter
        if "bucket" in args:
            valid_buckets = ["past", "overdue", "undated", "ungraded", "unsubmitted", "upcoming", "future"]
            if args["bucket"] not in valid_buckets:
                raise ValueError(f"bucket must be one of: {', '.join(valid_buckets)}")

        # Validate order_by
        if "orderBy" in args:
            valid_orders = ["position", "name", "due_at"]
            if args["orderBy"] not in valid_orders:
                raise ValueError(f"orderBy must be one of: {', '.join(valid_orders)}")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the list_assignments tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID

        Optional args:
            - bucket (str): Filter by bucket ("upcoming", "overdue", "past", etc.)
            - searchTerm (str): Search assignments by title
            - orderBy (str): Order results ("due_at", "name", "position")
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "courseId": <int>,
                "assignments": [<Assignment objects with all fields>],
                "total": <int>,
                "filters": {...}
            }
        """
        course_id = ctx.args["courseId"]

        # Extract optional filters
        bucket = ctx.args.get("bucket")
        search_term = ctx.args.get("searchTerm")
        order_by = ctx.args.get("orderBy", "due_at")
        per_page = ctx.args.get("perPage", 100)

        # Build include parameters for comprehensive data
        include_params = ASSIGNMENT_INCLUDE_ALL.copy()

        # Build query parameters
        params = build_assignment_params(
            include=include_params,
            bucket=bucket,
            search_term=search_term,
            order_by=order_by,
            override_assignment_dates=True,  # Apply overrides for accurate dates
            per_page=per_page,
        )

        # Fetch assignments with pagination
        assignments = await ctx.client.get(
            f"/courses/{course_id}/assignments",
            params=params,
            paginate=True,
        )

        return {
            "courseId": course_id,
            "assignments": assignments,
            "total": len(assignments),
            "filters": {
                "bucket": bucket,
                "searchTerm": search_term,
                "orderBy": order_by,
            },
        }
