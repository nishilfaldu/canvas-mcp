"""
Get Discussion Topic Tool

Fetches a single discussion topic by ID for a course.
Returns a full JSON discussion topic object.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool

@register_tool
class GetDiscussionTopicTool(BaseTool):
    """
    Get detailed info about a discussion topic.
    """
    name = "get_discussion_topic"
    description = (
        "Get details of a specific Canvas discussion topic (title, body, metadata, etc)."
    )
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
        topic = await ctx.client.get(f"/courses/{course_id}/discussion_topics/{topic_id}")
        return { "discussion_topic": topic }
