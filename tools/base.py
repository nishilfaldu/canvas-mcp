"""
Base tool class for Canvas MCP tools.
All tools should inherit from BaseTool and implement the execute() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from api.client import CanvasAPIClient


class ToolContext:
    """Context object passed to tool execute() methods."""

    def __init__(self, api_url: str, api_token: str, args: Dict[str, Any]):
        """
        Initialize tool context.

        Args:
            api_url: Canvas API base URL
            api_token: Canvas API access token
            args: Tool-specific arguments
        """
        self.api_url = api_url
        self.api_token = api_token
        self.args = args
        self._client: Optional[CanvasAPIClient] = None

    @property
    def client(self) -> CanvasAPIClient:
        """
        Get or create Canvas API client instance.

        Returns:
            CanvasAPIClient: Initialized API client

        Note:
            Client is lazily instantiated on first access
        """
        if self._client is None:
            self._client = CanvasAPIClient(self.api_url, self.api_token)
        return self._client


class BaseTool(ABC):
    """
    Abstract base class for all Canvas MCP tools.

    Each tool must:
    1. Define a unique name
    2. Provide a clear description
    3. Implement the execute() method

    Example:
        >>> class ListCoursesTool(BaseTool):
        ...     name = "list_courses"
        ...     description = "List all active courses for the user"
        ...
        ...     async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        ...         courses = await ctx.client.get("/courses")
        ...         return {"courses": courses}
    """

    # Tool metadata (must be overridden by subclasses)
    name: str = ""
    description: str = ""
    category: str = "general"  # "courses", "assignments", etc.

    @abstractmethod
    async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Execute the tool with given context.

        Args:
            ctx: Tool execution context with API client and arguments

        Returns:
            Tool result as a dictionary (will be converted to JSON)

        Raises:
            CanvasAPIError: On Canvas API errors
            ValueError: On invalid arguments

        Example:
            >>> async def execute(self, ctx: ToolContext) -> Dict[str, Any]:
            ...     course_id = ctx.args.get("courseId")
            ...     if not course_id:
            ...         raise ValueError("courseId is required")
            ...
            ...     course = await ctx.client.get(f"/courses/{course_id}")
            ...     return {"course": course}
        """
        pass

    def validate_args(self, args: Dict[str, Any]) -> None:
        """
        Validate tool arguments before execution.

        Override this method to add custom argument validation.

        Args:
            args: Arguments to validate

        Raises:
            ValueError: If arguments are invalid

        Example:
            >>> def validate_args(self, args: Dict[str, Any]) -> None:
            ...     if "courseId" not in args:
            ...         raise ValueError("courseId is required")
            ...     if not isinstance(args["courseId"], int):
            ...         raise ValueError("courseId must be an integer")
        """
        pass

    async def run(self, ctx: ToolContext) -> Dict[str, Any]:
        """
        Run the tool with validation and error handling.

        This method wraps execute() with:
        - Argument validation
        - Error handling
        - Consistent return format

        Args:
            ctx: Tool execution context

        Returns:
            Tool result dictionary

        Note:
            This method should NOT be overridden. Override execute() instead.
        """
        # Validate arguments
        self.validate_args(ctx.args)

        # Execute tool
        try:
            result = await self.execute(ctx)
            return result
        except Exception as e:
            # Re-raise to let main.py handle it
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' category='{self.category}'>"
