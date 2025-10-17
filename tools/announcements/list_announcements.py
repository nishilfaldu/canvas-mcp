"""
List Announcements Tool

Lists announcements across multiple courses for the student.
Returns full announcement data including title, message, and dates.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool
from utils.canvas_params import build_announcements_params


@register_tool
class ListAnnouncementsTool(BaseTool):
    """
    List announcements across multiple courses.

    Returns comprehensive announcement data including:
    - Announcement title and message
    - Post dates and delayed post dates
    - Course context (which course it belongs to)
    - Discussion topic details
    """

    name = "list_announcements"
    description = (
        "List announcements across one or more courses. "
        "Returns title, message, dates, and course context. "
        "Use when student asks 'What announcements do I have?' or 'Show me course announcements.'"
    )
    category = "announcements"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseIds" not in args:
            raise ValueError("courseIds is required")

        course_ids = args["courseIds"]
        if not isinstance(course_ids, list) or len(course_ids) == 0:
            raise ValueError("courseIds must be a non-empty list of course IDs")

        for course_id in course_ids:
            if not isinstance(course_id, int) or course_id <= 0:
                raise ValueError("All courseIds must be positive integers")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the list_announcements tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseIds (list[int]): List of Canvas course IDs to get announcements from

        Optional args:
            - startDate (str): Only return announcements after this date (ISO 8601)
            - endDate (str): Only return announcements before this date (ISO 8601)
            - activeOnly (bool): Only return published announcements (default: True)
            - latestOnly (bool): Only return most recent announcement per course
            - perPage (int): Results per page (default: 100)

        Returns:
            {
                "announcements": [<Announcement/DiscussionTopic objects>],
                "total": <int>,
                "courseIds": <list[int]>,
                "filters": {...}
            }
        """
        course_ids = ctx.args["courseIds"]

        # Convert course IDs to context codes (format: "course_123")
        context_codes = [f"course_{course_id}" for course_id in course_ids]

        # Extract optional filters
        start_date = ctx.args.get("startDate")
        end_date = ctx.args.get("endDate")
        active_only = ctx.args.get("activeOnly", True)
        latest_only = ctx.args.get("latestOnly")
        per_page = ctx.args.get("perPage", 100)

        # Build query parameters
        params = build_announcements_params(
            context_codes=context_codes,
            start_date=start_date,
            end_date=end_date,
            active_only=active_only,
            latest_only=latest_only,
            per_page=per_page,
        )

        # Fetch announcements with pagination
        announcements = await ctx.client.get(
            "/announcements",
            params=params,
            paginate=True,
        )

        return {
            "announcements": announcements,
            "total": len(announcements),
            "courseIds": course_ids,
            "filters": {
                "startDate": start_date,
                "endDate": end_date,
                "activeOnly": active_only,
                "latestOnly": latest_only,
            },
        }
