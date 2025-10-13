"""
Preview HTML Tool

Previews HTML content within a course context.
Useful for rendering course-specific HTML before posting.
"""

from typing import Any, Dict
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool


@register_tool
class PreviewHtmlTool(BaseTool):
    """
    Preview HTML content with course context.

    Takes HTML content and renders it with course-specific context
    (e.g., resolves course links, applies course styling).

    Useful for previewing discussion posts, announcements, or other
    HTML content before submitting it.
    """

    name = "preview_html"
    description = (
        "Preview HTML content with course context. "
        "Renders HTML with course-specific links and styling. "
        "Use when student wants to preview how HTML will look in the course."
    )
    category = "courses"

    def validate_args(self, args: Dict[str, Any]) -> None:
        """Validate tool arguments."""
        if "courseId" not in args:
            raise ValueError("courseId is required")

        course_id = args["courseId"]
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("courseId must be a positive integer")

        if "html" not in args:
            raise ValueError("html is required")

        html = args["html"]
        if not isinstance(html, str) or not html.strip():
            raise ValueError("html must be a non-empty string")

    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the preview_html tool.

        Args:
            ctx: Tool execution context

        Required args:
            - courseId (int): Canvas course ID for context
            - html (str): HTML content to preview

        Returns:
            {
                "courseId": <int>,
                "html": <str>,  # Rendered HTML
                "originalHtml": <str>  # Original input HTML
            }
        """
        course_id = ctx.args["courseId"]
        html_content = ctx.args["html"]

        # Send POST request to preview endpoint
        result = await ctx.client.post(
            f"/courses/{course_id}/preview_html",
            json_data={"html": html_content},
        )

        # Canvas returns the rendered HTML in 'html' field
        rendered_html = result.get("html", html_content)

        return {
            "courseId": course_id,
            "html": rendered_html,
            "originalHtml": html_content,
        }
