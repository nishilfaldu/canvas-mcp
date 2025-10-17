"""
Canvas MCP tools package.

All tools are automatically registered via the @register_tool decorator.
Import this package to register all available tools.
"""

from .base import BaseTool, ToolContext
from .registry import registry, register_tool

# Import all tool modules to trigger registration
from .courses import (
    list_courses,
    get_course,
    get_course_progress,
    get_course_users,
    preview_html,
)
from .announcements import list_announcements
from .assignments import list_assignments, get_assignment, get_assignment_submission
from .enrollments import list_enrollments
from .quizzes import list_quizzes, get_quiz, get_quiz_submission, list_quiz_submissions
from .discussions import *

__all__ = [
    "BaseTool",
    "ToolContext",
    "registry",
    "register_tool",
]
