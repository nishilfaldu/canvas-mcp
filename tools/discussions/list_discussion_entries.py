"""
List Discussion Entries Tool

Lists all entries (posts/replies) for a given discussion topic.
Returns full JSON entry objects.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool

@register_tool
class ListDiscussionEntriesTool(BaseTool):
    """
    List all entries (posts/replies) in a discussion topic.
    """
    name = "list_discussion_entries"
    description = "List all top-level posts and replies in a discussion topic."
    category = "discussions"

    def validate_args(self, args: Dict[str, Any]) -> None:
        if "course_id" not in args or "topic_id" not in args:
            raise ValueError("course_id and topic_id are required")
        if not isinstance(args["course_id"], (str, int)):
            raise ValueError("course_id must be str or int")
        if not isinstance(args["topic_id"], (str, int)):
            raise ValueError("topic_id must be str or int")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        course_id = ctx.args["course_id"]
        topic_id = ctx.args["topic_id"]
        entries = await ctx.client.get(f"/courses/{course_id}/discussion_topics/{topic_id}/entries", paginate=True)
        return { "discussion_entries": entries, "total": len(entries) }
