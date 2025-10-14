"""
List Quizzes Tool

Lists all quizzes for a specific course.
Returns comprehensive quiz data including title, description, time limits, and points.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_quiz_params


@register_tool
class ListQuizzesTool(BaseTool):
    """
    List all quizzes for a specific course.

    Returns comprehensive quiz data including:
    - Quiz title and description
    - Time limits and allowed attempts
    - Question count and points possible
    - Due dates and lock dates
    - Quiz type and settings
    """

    name = "list_quizzes"
    description = (
        "List all quizzes for a specific Canvas course. "
        "Returns title, description, time limits, question count, points possible, and due dates. "
        "Use when student asks 'What quizzes do I have?' or 'Show me quizzes for this course.'"
    )
    category = "quizzes"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the list_quizzes tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID to list quizzes from

        Optional args:
            - searchTerm (str): Search quizzes by partial title match
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "courseId": <int>,
                "quizzes": [<Quiz objects>],
                "total": <int>,
                "filters": {...}
            }
        """
        course_id = ctx.args["courseId"]
        search_term = ctx.args.get("searchTerm")
        per_page = ctx.args.get("perPage", 100)

        # Build query parameters
        params = build_quiz_params(
            search_term=search_term,
            per_page=per_page,
        )

        # Fetch quizzes with pagination
        quizzes = await ctx.client.get(
            f"/courses/{course_id}/quizzes",
            params=params,
            paginate=True,
        )

        return {
            "courseId": course_id,
            "quizzes": quizzes,
            "total": len(quizzes),
            "filters": {
                "searchTerm": search_term,
            },
        }
