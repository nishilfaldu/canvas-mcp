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


# Comprehensive list of all available include[] parameters for assignments
ASSIGNMENT_INCLUDE_ALL = [
    "submission",              # Current user's submission
    "assignment_visibility",   # Array of student IDs who can see this assignment
    "all_dates",              # All date objects (base and overrides)
    "overrides",              # Assignment override structures
    "observed_users",         # Observed users submissions (for observers)
    "can_edit",               # Whether user can edit assignment
    "score_statistics",       # Min, max, mean scores for assignment
    "ab_guid",                # Academic benchmark IDs
]


def build_assignment_params(
    include: Optional[List[str]] = None,
    search_term: Optional[str] = None,
    override_assignment_dates: Optional[bool] = None,
    needs_grading_count_by_section: Optional[bool] = None,
    bucket: Optional[str] = None,
    assignment_ids: Optional[List[int]] = None,
    order_by: Optional[str] = None,
    post_to_sis: Optional[bool] = None,
    per_page: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build query parameters for assignments list endpoint.

    Args:
        include: List of additional data to include (use ASSIGNMENT_INCLUDE_ALL for everything)
        search_term: The partial title of the assignments to match and return
        override_assignment_dates: Apply assignment overrides to return dates
        needs_grading_count_by_section: Split up needs_grading_count by section
        bucket: Filter by assignment bucket ("past", "overdue", "undated", "ungraded",
                "unsubmitted", "upcoming", "future")
        assignment_ids: List of specific assignment IDs to return
        order_by: Order results by field ("position", "name", "due_at")
        post_to_sis: Only return assignments that have post_to_sis set
        per_page: Number of results per page

    Returns:
        Dictionary of query parameters ready for Canvas API

    Example:
        >>> params = build_assignment_params(
        ...     include=["submission", "score_statistics"],
        ...     bucket="upcoming",
        ...     order_by="due_at",
        ...     per_page=50
        ... )
    """
    params: Dict[str, Any] = {}

    # Include parameters
    if include:
        params["include[]"] = include

    # Search/filter parameters
    if search_term:
        params["search_term"] = search_term

    if override_assignment_dates is not None:
        params["override_assignment_dates"] = str(override_assignment_dates).lower()

    if needs_grading_count_by_section is not None:
        params["needs_grading_count_by_section"] = str(needs_grading_count_by_section).lower()

    if bucket:
        params["bucket"] = bucket

    if assignment_ids:
        params["assignment_ids[]"] = assignment_ids

    if order_by:
        params["order_by"] = order_by

    if post_to_sis is not None:
        params["post_to_sis"] = str(post_to_sis).lower()

    # Pagination
    if per_page:
        params["per_page"] = per_page

    return params


def build_single_assignment_params(
    include: Optional[List[str]] = None,
    override_assignment_dates: Optional[bool] = None,
    needs_grading_count_by_section: Optional[bool] = None,
    all_dates: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Build query parameters for single assignment detail endpoint.

    Args:
        include: List of additional data to include
        override_assignment_dates: Apply assignment overrides to dates
        needs_grading_count_by_section: Split needs_grading_count by section
        all_dates: Return all dates associated with assignment

    Returns:
        Dictionary of query parameters

    Example:
        >>> params = build_single_assignment_params(
        ...     include=["submission", "score_statistics", "overrides"],
        ...     override_assignment_dates=True
        ... )
    """
    params: Dict[str, Any] = {}

    if include:
        params["include[]"] = include

    if override_assignment_dates is not None:
        params["override_assignment_dates"] = str(override_assignment_dates).lower()

    if needs_grading_count_by_section is not None:
        params["needs_grading_count_by_section"] = str(needs_grading_count_by_section).lower()

    if all_dates is not None:
        params["all_dates"] = str(all_dates).lower()

    return params
