"""
Utility functions for building Canvas API parameters.
Helps construct include[] arrays and other query parameters.
"""

from typing import Any, Dict, List, Optional


# Comprehensive list of all available include[] parameters for courses
COURSE_INCLUDE_ALL = [
    "syllabus_body",         # Full HTML syllabus
    "term",                  # Enrollment term details
    "course_progress",       # Student's progress tracking
    "total_scores",          # Grade scores in enrollments
    "current_grading_period_scores",  # Current grading period scores
    "grading_periods",       # All grading periods
    "permissions",           # User's permissions in course
    "sections",              # Course sections
    "favorites",             # Whether course is favorited
    "public_description",    # Public course description
    "total_students",        # Count of active students
    "needs_grading_count",   # Submissions needing grading (instructor only)
    "account",               # Parent account info
    "course_image",          # Course image URL
    "banner_image",          # Course banner image
    "concluded",             # Whether course is concluded
    "tabs",                  # Course navigation tabs
    "passback_status",       # Grade passback status
    "observed_users",        # Observed users (for observers)
]


def build_course_params(
    include: Optional[List[str]] = None,
    enrollment_state: Optional[str] = None,
    enrollment_type: Optional[str] = None,
    state: Optional[List[str]] = None,
    homeroom: Optional[bool] = None,
    per_page: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build query parameters for course list endpoints.

    Args:
        include: List of additional data to include (e.g., ["syllabus_body", "term"])
                 Use COURSE_INCLUDE_ALL for comprehensive data
        enrollment_state: Filter by enrollment state ("active", "invited_or_pending", "completed")
        enrollment_type: Filter by enrollment type ("teacher", "student", "ta", "observer", "designer")
        state: Filter by course state (["available"], ["completed"], etc.)
        homeroom: Return only homeroom courses
        per_page: Number of results per page

    Returns:
        Dictionary of query parameters ready for Canvas API

    Example:
        >>> params = build_course_params(
        ...     include=["syllabus_body", "term", "total_scores"],
        ...     enrollment_state="active",
        ...     per_page=50
        ... )
        >>> # Results in: ?include[]=syllabus_body&include[]=term&include[]=total_scores&enrollment_state=active&per_page=50
    """
    params: Dict[str, Any] = {}

    # Include parameters (Canvas uses include[] format)
    if include:
        params["include[]"] = include

    # Enrollment filters
    if enrollment_state:
        params["enrollment_state"] = enrollment_state

    if enrollment_type:
        params["enrollment_type"] = enrollment_type

    # State filters
    if state:
        params["state[]"] = state

    # Homeroom filter
    if homeroom is not None:
        params["homeroom"] = str(homeroom).lower()

    # Pagination
    if per_page:
        params["per_page"] = per_page

    return params


def build_course_user_params(
    enrollment_type: Optional[List[str]] = None,
    enrollment_state: Optional[List[str]] = None,
    include: Optional[List[str]] = None,
    per_page: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build query parameters for course users endpoint.

    Args:
        enrollment_type: Filter by enrollment types (["student"], ["teacher"], etc.)
        enrollment_state: Filter by enrollment states (["active"], ["completed"], etc.)
        include: Additional data to include (["email", "avatar_url", "enrollments"])
        per_page: Number of results per page

    Returns:
        Dictionary of query parameters ready for Canvas API

    Example:
        >>> params = build_course_user_params(
        ...     enrollment_type=["student"],
        ...     enrollment_state=["active"],
        ...     include=["email", "avatar_url"]
        ... )
    """
    params: Dict[str, Any] = {}

    if enrollment_type:
        params["enrollment_type[]"] = enrollment_type

    if enrollment_state:
        params["enrollment_state[]"] = enrollment_state

    if include:
        params["include[]"] = include

    if per_page:
        params["per_page"] = per_page

    return params


def build_single_course_params(
    include: Optional[List[str]] = None,
    teacher_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build query parameters for single course detail endpoint.

    Args:
        include: List of additional data to include
        teacher_limit: Maximum number of teachers to include in response

    Returns:
        Dictionary of query parameters

    Example:
        >>> params = build_single_course_params(
        ...     include=["syllabus_body", "term", "permissions"],
        ...     teacher_limit=5
        ... )
    """
    params: Dict[str, Any] = {}

    if include:
        params["include[]"] = include

    if teacher_limit:
        params["teacher_limit"] = teacher_limit

    return params
