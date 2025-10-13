"""
Tool registry system for automatic tool discovery and registration.
"""

from typing import Dict, List, Type
from .base import BaseTool


class ToolRegistry:
    """
    Registry for managing all Canvas MCP tools.

    Tools are automatically registered when they're imported.
    The registry provides lookup by name and listing by category.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tools_by_category: Dict[str, List[BaseTool]] = {}

    def register(self, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class.

        Args:
            tool_class: Tool class to register (must inherit from BaseTool)

        Raises:
            ValueError: If tool name is empty or already registered

        Example:
            >>> registry.register(ListCoursesTool)
        """
        # Instantiate the tool
        tool = tool_class()

        if not tool.name:
            raise ValueError(f"Tool {tool_class.__name__} must define a name")

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        # Register tool
        self._tools[tool.name] = tool

        # Add to category index
        category = tool.category
        if category not in self._tools_by_category:
            self._tools_by_category[category] = []
        self._tools_by_category[category].append(tool)

    def get(self, name: str) -> BaseTool:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance

        Raises:
            KeyError: If tool not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found. Available: {list(self._tools.keys())}")
        return self._tools[name]

    def list_all(self) -> List[BaseTool]:
        """
        Get list of all registered tools.

        Returns:
            List of tool instances
        """
        return list(self._tools.values())

    def list_by_category(self, category: str) -> List[BaseTool]:
        """
        Get list of tools in a specific category.

        Args:
            category: Category name (e.g., "courses", "assignments")

        Returns:
            List of tool instances in that category
        """
        return self._tools_by_category.get(category, [])

    def list_tool_names(self) -> List[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names

        Example:
            >>> registry.list_tool_names()
            ['list_courses', 'get_course', 'get_course_progress', ...]
        """
        return list(self._tools.keys())

    def get_categories(self) -> List[str]:
        """
        Get list of all categories.

        Returns:
            List of category names
        """
        return list(self._tools_by_category.keys())


# Global registry instance
registry = ToolRegistry()


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator for registering tool classes.

    Usage:
        >>> @register_tool
        ... class ListCoursesTool(BaseTool):
        ...     name = "list_courses"
        ...     description = "List all courses"
        ...     async def execute(self, ctx):
        ...         ...

    Args:
        tool_class: Tool class to register

    Returns:
        Same tool class (unmodified)
    """
    registry.register(tool_class)
    return tool_class
