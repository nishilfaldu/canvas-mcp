"""
Get Quiz Tool

Gets detailed information about a specific quiz.
Returns comprehensive quiz data including all settings and restrictions.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool


@register_tool
class GetQuizTool(BaseTool):
    """
    Get detailed information about a specific quiz.

    Returns comprehensive quiz data including:
    - Quiz title and description (HTML)
    - Time limits and allowed attempts
    - Question count and points possible
    - Due dates, lock dates, and unlock dates
    - Access restrictions and IP filters
    - Quiz type (practice, assignment, graded survey, etc.)
    - Scoring policy and shuffle settings
    """

    name = "get_quiz"
    description = (
        "Get detailed information about a specific quiz by ID. "
        "Returns comprehensive data including description, time limits, question count, "
        "points, due dates, and access restrictions. "
        "Use when student asks 'Tell me about this quiz' or 'What's the format of quiz X?'"
    )
    category = "quizzes"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")
        if "quizId" not in args:
            raise ValueError("quizId is required")

        course_id = args["courseId"]
        quiz_id = args["quizId"]

        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")
        if not isinstance(quiz_id, int) or quiz_id <= 0:
            raise ValueError("quizId must be a positive integer")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the get_quiz tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID
            - quizId (int): Canvas quiz ID

        Returns:
            {
                "courseId": <int>,
                "quizId": <int>,
                "quiz": <Quiz object>
            }
        """
        course_id = ctx.args["courseId"]
        quiz_id = ctx.args["quizId"]

        # Fetch quiz details
        quiz = await ctx.client.get(
            f"/courses/{course_id}/quizzes/{quiz_id}",
        )

        return {
            "courseId": course_id,
            "quizId": quiz_id,
            "quiz": quiz,
        }
