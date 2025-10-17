"""
List Discussion Topics Tool

Lists all discussion topics for a given course.
Returns full JSON discussion topic objects.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool

@register_tool
class ListDiscussionTopicsTool(BaseTool):
    """
    List all discussion topics for a course.
    """
    name = "list_discussion_topics"
    description = (
        "List all discussion topics for a Canvas course. "
        "Returns basic metadata plus post status, unread state, etc."
    )
    category = "discussions"

    def validate_args(self, args: Dict[str, Any]) -> None:
        if "course_id" not in args:
            raise ValueError("course_id is required")
        if not isinstance(args["course_id"], (str, int)):
            raise ValueError("course_id must be str or int")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        course_id = ctx.args["course_id"]
        params = { "per_page": 50 }  # Default pagination, API allows ?page= etc.
        # Add more params as needed in the future
        discussion_topics = await ctx.client.get(f"/courses/{course_id}/discussion_topics", params=params, paginate=True)
        return { "discussion_topics": discussion_topics, "total": len(discussion_topics) }
