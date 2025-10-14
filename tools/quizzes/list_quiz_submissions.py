"""
List Quiz Submissions Tool

Lists quiz submissions for a specific quiz.
For students, this will only return their own submission(s).
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_quiz_submission_params, QUIZ_SUBMISSION_INCLUDE_ALL


@register_tool
class ListQuizSubmissionsTool(BaseTool):
    """
    List quiz submissions for a specific quiz.

    For students, this endpoint will only return their own submission(s).
    Returns comprehensive submission data including:
    - Submission status and scores
    - Attempt information
    - Time spent on the quiz
    - Associated Canvas submissions
    """

    name = "list_quiz_submissions"
    description = (
        "List quiz submissions for a specific quiz. "
        "Students will only see their own submissions. "
        "Returns submission status, scores, and attempt information. "
        "Use when student asks 'Show me my quiz attempts' or 'What are my quiz submissions?'"
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
        Execute the list_quiz_submissions tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID
            - quizId (int): Canvas quiz ID

        Returns:
            {
                "courseId": <int>,
                "quizId": <int>,
                "submissions": [<QuizSubmission objects>],
                "total": <int>
            }
        """
        course_id = ctx.args["courseId"]
        quiz_id = ctx.args["quizId"]

        # Build parameters to include all submission data
        params = build_quiz_submission_params(
            include=QUIZ_SUBMISSION_INCLUDE_ALL,
        )

        # Fetch quiz submissions
        # Note: For students, this will only return their own submissions
        submissions = await ctx.client.get(
            f"/courses/{course_id}/quizzes/{quiz_id}/submissions",
            params=params,
            paginate=True,
        )

        return {
            "courseId": course_id,
            "quizId": quiz_id,
            "submissions": submissions,
            "total": len(submissions),
        }
