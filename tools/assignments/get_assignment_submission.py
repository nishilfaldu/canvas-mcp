"""
Get Assignment Submission Tool

Fetches the student's submission for a specific assignment.
Returns comprehensive submission data including grades, comments, and attachments.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool


@register_tool
class GetAssignmentSubmissionTool(BaseTool):
    """
    Get the student's submission for a specific assignment.

    Returns comprehensive submission data including:
    - Submission status (submitted, graded, late, missing)
    - Grade and score information
    - Submission comments and feedback
    - Attached files and URLs
    - Submission history
    - Rubric assessment
    """

    name = "get_assignment_submission"
    description = (
        "Get the student's submission for a specific assignment. "
        "Returns submission status, grade, feedback, attachments, and rubric assessment. "
        "Use when student asks 'What did I submit?' or 'What's my grade on this assignment?'"
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
        Execute the get_assignment_submission tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID
            - assignmentId (int): Canvas assignment ID

        Returns:
            {
                "courseId": <int>,
                "assignmentId": <int>,
                "submission": <Submission object with all fields>
            }
        """
        course_id = ctx.args["courseId"]
        assignment_id = ctx.args["assignmentId"]

        # Build include parameters for comprehensive submission data
        include_params = [
            "submission_history",   # All submission attempts
            "submission_comments",  # Teacher/peer comments
            "rubric_assessment",    # Rubric scores if applicable
            "full_rubric_assessment",  # Detailed rubric with comments
            "visibility",           # Visibility settings
            "course",               # Course info
            "user",                 # Student user info
        ]

        params = {
            "include[]": include_params,
        }

        # Fetch submission for the current user (self)
        # Canvas returns the submission for the authenticated user
        submission = await ctx.client.get(
            f"/courses/{course_id}/assignments/{assignment_id}/submissions/self",
            params=params,
        )

        return {
            "courseId": course_id,
            "assignmentId": assignment_id,
            "submission": submission,
        }
