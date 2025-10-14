"""
List Enrollments Tool

Lists all enrollments for the student with grade information.
Returns comprehensive enrollment and grade data across all courses.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_enrollments_params, ENROLLMENT_INCLUDE_ALL


@register_tool
class ListEnrollmentsTool(BaseTool):
    """
    List all enrollments for the student with grades.

    Returns comprehensive enrollment and grade data including:
    - Current and final grades
    - Current and final scores
    - Current points earned
    - Enrollment status and type
    - Course information
    - Grading period data
    """

    name = "list_enrollments"
    description = (
        "List all enrollments for the student with comprehensive grade information. "
        "Returns current grades, final grades, scores, and points across all courses. "
        "Use when student asks 'What are my grades?' or 'Show me all my course grades.'"
    )
    category = "enrollments"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        # Validate state filter
        if "state" in args:
            if not isinstance(args["state"], list):
                raise ValueError("state must be a list")
            valid_states = ["active", "invited_or_pending", "creation_pending", "deleted", "rejected", "completed", "inactive"]
            for state in args["state"]:
                if state not in valid_states:
                    raise ValueError(f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}")

        # Validate enrollment type filter
        if "enrollmentType" in args:
            if not isinstance(args["enrollmentType"], list):
                raise ValueError("enrollmentType must be a list")
            valid_types = ["StudentEnrollment", "TeacherEnrollment", "TaEnrollment", "DesignerEnrollment", "ObserverEnrollment"]
            for etype in args["enrollmentType"]:
                if etype not in valid_types:
                    raise ValueError(f"Invalid enrollmentType '{etype}'. Must be one of: {', '.join(valid_types)}")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the list_enrollments tool.

        Args:
            ctx: Tool execution context

        Optional args:
            - state (list[str]): Filter by enrollment state (default: ["active"])
            - enrollmentType (list[str]): Filter by type (default: ["StudentEnrollment"])
            - gradingPeriodId (int): Return grades for specific grading period
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "enrollments": [<Enrollment objects with grade data>],
                "total": <int>,
                "filters": {...}
            }
        """
        # Extract optional filters
        state = ctx.args.get("state", ["active"])
        enrollment_type = ctx.args.get("enrollmentType", ["StudentEnrollment"])
        grading_period_id = ctx.args.get("gradingPeriodId")
        per_page = ctx.args.get("perPage", 100)

        # Build include parameters for comprehensive grade data
        include_params = ENROLLMENT_INCLUDE_ALL.copy()

        # Build query parameters
        params = build_enrollments_params(
            user_id="self",  # Always get current user's enrollments
            state=state,
            enrollment_type=enrollment_type,
            include=include_params,
            grading_period_id=grading_period_id,
            per_page=per_page,
        )

        # Fetch enrollments with pagination
        enrollments = await ctx.client.get(
            "/users/self/enrollments",
            params=params,
            paginate=True,
        )

        return {
            "enrollments": enrollments,
            "total": len(enrollments),
            "filters": {
                "state": state,
                "enrollmentType": enrollment_type,
                "gradingPeriodId": grading_period_id,
            },
        }
