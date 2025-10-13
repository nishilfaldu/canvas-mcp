"""
Get Course Users Tool

Lists users (students/classmates) in a specific course.
Respects course privacy settings - only shows what the student can see.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils import build_course_user_params


@register_tool
class GetCourseUsersTool(BaseTool):
    """
    List users in a specific course.

    By default, returns students in the course (classmates).
    Students can only see what their course permissions allow.

    Returns user information including:
    - Name and sortable name
    - Avatar URL
    - Email (if visible)
    - Enrollment information
    """

    name = "get_course_users"
    description = (
        "List users in a specific course (typically classmates). "
        "Returns names, avatars, and enrollment info based on course privacy settings. "
        "Use when student asks 'Who is in my class?' or 'List my classmates.'"
    )
    category = "courses"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

        # Validate enrollment type filter
        if "enrollmentType" in args:
            enrollment_type = args["enrollmentType"]
            if not isinstance(enrollment_type, list):
                raise ValueError("enrollmentType must be a list")

            valid_types = ["student", "teacher", "ta", "observer", "designer"]
            for etype in enrollment_type:
                if etype not in valid_types:
                    raise ValueError(
                        f"Invalid enrollment type '{etype}'. Must be one of: {', '.join(valid_types)}"
                    )

        # Validate enrollment state filter
        if "enrollmentState" in args:
            enrollment_state = args["enrollmentState"]
            if not isinstance(enrollment_state, list):
                raise ValueError("enrollmentState must be a list")

            valid_states = ["active", "invited", "rejected", "completed", "inactive"]
            for estate in enrollment_state:
                if estate not in valid_states:
                    raise ValueError(
                        f"Invalid enrollment state '{estate}'. Must be one of: {', '.join(valid_states)}"
                    )

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the get_course_users tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID

        Optional args:
            - enrollmentType (list[str]): Filter by types (default: ["student"])
            - enrollmentState (list[str]): Filter by states (default: ["active"])
            - includeEmail (bool): Include email addresses (default: True, respects privacy)
            - includeAvatar (bool): Include avatar URLs (default: True)
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "courseId": <int>,
                "users": [<User objects>],
                "total": <int>,
                "filters": {
                    "enrollmentType": <list>,
                    "enrollmentState": <list>
                }
            }
        """
        course_id = ctx.args["courseId"]

        # Extract filters with defaults
        enrollment_type = ctx.args.get("enrollmentType", ["student"])
        enrollment_state = ctx.args.get("enrollmentState", ["active"])
        include_email = ctx.args.get("includeEmail", True)
        include_avatar = ctx.args.get("includeAvatar", True)
        per_page = ctx.args.get("perPage", 100)

        # Build include parameters
        include_params = ["enrollments"]  # Always include enrollment info
        if include_email:
            include_params.append("email")
        if include_avatar:
            include_params.append("avatar_url")

        # Build query parameters
        params = build_course_user_params(
            enrollment_type=enrollment_type,
            enrollment_state=enrollment_state,
            include=include_params,
            per_page=per_page,
        )

        # Fetch course users with pagination
        users = await ctx.client.get(
            f"/courses/{course_id}/users",
            params=params,
            paginate=True,
        )

        return {
            "courseId": course_id,
            "users": users,
            "total": len(users),
            "filters": {
                "enrollmentType": enrollment_type,
                "enrollmentState": enrollment_state,
            },
        }
