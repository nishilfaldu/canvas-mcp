"""
List Entry Replies Tool

Lists all direct replies to a top-level discussion entry.
Returns paginated JSON reply objects.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool

@register_tool
class ListEntryRepliesTool(BaseTool):
    """
    List replies to a top-level entry in a discussion topic (newest first).
    """
    name = "list_entry_replies"
    description = (
        "Retrieve all replies to a top-level discussion entry in a topic, newest first."
    )
    category = "discussions"

    def validate_args(self, args: Dict[str, Any]) -> None:
        for field in ["course_id", "topic_id", "entry_id"]:
            if field not in args:
                raise ValueError(f"{field} is required")
            if not isinstance(args[field], (str, int)):
                raise ValueError(f"{field} must be str or int")
    
    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        course_id = ctx.args["course_id"]
        topic_id = ctx.args["topic_id"]
        entry_id = ctx.args["entry_id"]
        replies = await ctx.client.get(
            f"/courses/{course_id}/discussion_topics/{topic_id}/entries/{entry_id}/replies",
            paginate=True,
        )
        return { "entry_replies": replies, "total": len(replies) }
