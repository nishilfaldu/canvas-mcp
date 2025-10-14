"""
Get Quiz Submission Tool

Gets the student's own quiz submission for a specific quiz.
Returns submission status, score, and attempt information.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_quiz_submission_params, QUIZ_SUBMISSION_INCLUDE_ALL


@register_tool
class GetQuizSubmissionTool(BaseTool):
    """
    Get the student's own submission for a specific quiz.

    Returns comprehensive submission data including:
    - Submission status (complete, pending_review, etc.)
    - Score and points earned
    - Attempt number and submission time
    - Time spent on the quiz
    - Associated Canvas submission
    - Quiz details
    """

    name = "get_quiz_submission"
    description = (
        "Get the student's own submission for a specific quiz. "
        "Returns submission status, score, attempt information, and time spent. "
        "Use when student asks 'What did I get on this quiz?' or 'What's my quiz submission status?'"
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
        Execute the get_quiz_submission tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID
            - quizId (int): Canvas quiz ID

        Returns:
            {
                "courseId": <int>,
                "quizId": <int>,
                "submission": <QuizSubmission object>
            }
        """
        course_id = ctx.args["courseId"]
        quiz_id = ctx.args["quizId"]

        # Build parameters to include all submission data
        params = build_quiz_submission_params(
            include=QUIZ_SUBMISSION_INCLUDE_ALL,
        )

        # Fetch the current user's quiz submission
        # Note: This endpoint returns the submission for the authenticated user
        submission = await ctx.client.get(
            f"/courses/{course_id}/quizzes/{quiz_id}/submission",
            params=params,
        )

        return {
            "courseId": course_id,
            "quizId": quiz_id,
            "submission": submission,
        }
