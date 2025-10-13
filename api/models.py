"""
Pydantic models for Canvas API data structures.
Comprehensive type definitions for all course-related responses.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Tool Request/Response Models ====================

class ToolRequest(BaseModel):
    """Request format for MCP tool calls."""

    tool: str = Field(description="Name of the tool to execute")
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    canvasApiUrl: str = Field(description="Canvas API base URL")
    canvasApiToken: str = Field(description="Canvas API access token")


class ToolResponse(BaseModel):
    """Response format for MCP tool calls."""

    result: Any = Field(description="Tool execution result (usually dict or list)")
    error: Optional[str] = Field(default=None, description="Error message if tool failed")


# ==================== Canvas Core Models ====================

class EnrollmentGrades(BaseModel):
    """Grade information for an enrollment."""

    html_url: Optional[str] = None
    current_score: Optional[float] = None
    current_grade: Optional[str] = None
    final_score: Optional[float] = None
    final_grade: Optional[str] = None
    unposted_current_score: Optional[float] = None
    unposted_current_grade: Optional[str] = None
    unposted_final_score: Optional[float] = None
    unposted_final_grade: Optional[str] = None


class Enrollment(BaseModel):
    """Student enrollment information."""

    id: int
    user_id: int
    course_id: int
    type: str  # "StudentEnrollment", "TeacherEnrollment", etc.
    enrollment_state: str  # "active", "invited", "inactive"
    role: str
    role_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    total_activity_time: Optional[int] = None
    grades: Optional[EnrollmentGrades] = None
    # Additional computed scores
    computed_current_score: Optional[float] = None
    computed_final_score: Optional[float] = None
    computed_current_grade: Optional[str] = None
    computed_final_grade: Optional[str] = None
    # Current grading period scores
    current_grading_period_id: Optional[int] = None
    current_grading_period_title: Optional[str] = None
    current_period_computed_current_score: Optional[float] = None
    current_period_computed_final_score: Optional[float] = None
    current_period_computed_current_grade: Optional[str] = None
    current_period_computed_final_grade: Optional[str] = None


class Term(BaseModel):
    """Enrollment term information."""

    id: int
    name: str
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    workflow_state: Optional[str] = None
    grading_period_group_id: Optional[int] = None
    sis_term_id: Optional[str] = None
    sis_import_id: Optional[int] = None
    overrides: Optional[Dict[str, Any]] = None


class GradingPeriod(BaseModel):
    """Grading period information."""

    id: int
    title: str
    start_date: datetime
    end_date: datetime
    close_date: Optional[datetime] = None
    weight: Optional[float] = None
    is_closed: bool = False


class CourseCalendar(BaseModel):
    """Course calendar information."""

    ics: str  # ICS feed URL


class Section(BaseModel):
    """Course section information."""

    id: int
    name: str
    course_id: int
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    enrollment_role: Optional[str] = None
    restrict_enrollments_to_section_dates: Optional[bool] = None
    nonxlist_course_id: Optional[int] = None
    sis_section_id: Optional[str] = None
    sis_course_id: Optional[str] = None
    integration_id: Optional[str] = None
    sis_import_id: Optional[int] = None


class CoursePermissions(BaseModel):
    """User permissions within a course."""

    create_discussion_topic: bool = False
    create_announcement: bool = False


class CourseProgress(BaseModel):
    """Student's progress in a course."""

    requirement_count: int = 0
    requirement_completed_count: int = 0
    next_requirement_url: Optional[str] = None
    completed_at: Optional[datetime] = None


class Course(BaseModel):
    """
    Complete Canvas Course object with all possible fields.
    This includes all data that can be returned via include[] parameters.
    """

    # Core fields
    id: int
    name: str
    course_code: str
    workflow_state: Literal["unpublished", "available", "completed", "deleted"]
    account_id: int
    root_account_id: int
    enrollment_term_id: int

    # Optional core fields
    uuid: Optional[str] = None
    sis_course_id: Optional[str] = None
    integration_id: Optional[str] = None
    sis_import_id: Optional[int] = None

    # Dates
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    restrict_enrollments_to_course_dates: Optional[bool] = None

    # Display settings
    default_view: Optional[Literal["feed", "wiki", "modules", "assignments", "syllabus"]] = None
    locale: Optional[str] = None
    time_zone: Optional[str] = None
    blueprint: Optional[bool] = None
    blueprint_restrictions: Optional[Dict[str, Any]] = None
    blueprint_restrictions_by_object_type: Optional[Dict[str, Any]] = None

    # Student metadata
    total_students: Optional[int] = None

    # Course settings
    is_public: Optional[bool] = None
    is_public_to_auth_users: Optional[bool] = None
    public_syllabus: Optional[bool] = None
    public_syllabus_to_auth: Optional[bool] = None
    public_description: Optional[str] = None
    storage_quota_mb: Optional[int] = None
    storage_quota_used_mb: Optional[int] = None
    hide_final_grades: Optional[bool] = None
    license: Optional[str] = None
    allow_student_assignment_edits: Optional[bool] = None
    allow_wiki_comments: Optional[bool] = None
    allow_student_forum_attachments: Optional[bool] = None
    open_enrollment: Optional[bool] = None
    self_enrollment: Optional[bool] = None
    restrict_student_past_view: Optional[bool] = None
    restrict_student_future_view: Optional[bool] = None
    restrict_quantitative_data: Optional[bool] = None

    # Grading settings
    grading_standard_id: Optional[int] = None
    grade_passback_setting: Optional[str] = None
    apply_assignment_group_weights: Optional[bool] = None

    # Rich content (via include[])
    syllabus_body: Optional[str] = None  # HTML content
    calendar: Optional[CourseCalendar] = None
    needs_grading_count: Optional[int] = None  # Only for instructors

    # Related objects (via include[])
    term: Optional[Term] = None
    enrollments: Optional[List[Enrollment]] = None
    permissions: Optional[CoursePermissions] = None
    course_progress: Optional[CourseProgress] = None
    grading_periods: Optional[List[GradingPeriod]] = None
    sections: Optional[List[Section]] = None

    # Nickname support
    original_name: Optional[str] = None  # Shown if user set a nickname

    # Access settings
    access_restricted_by_date: Optional[bool] = None
    course_format: Optional[str] = None
    enrollment_role: Optional[str] = None

    # HomeRoom
    homeroom_course: Optional[bool] = None
    homeroom_course_id: Optional[int] = None

    # Additional metadata
    is_favorite: Optional[bool] = None
    friendly_name: Optional[str] = None

    # Pacing
    enable_course_paces: Optional[bool] = None


class User(BaseModel):
    """Canvas user information."""

    id: int
    name: str
    created_at: Optional[datetime] = None
    sortable_name: Optional[str] = None
    short_name: Optional[str] = None
    sis_user_id: Optional[str] = None
    integration_id: Optional[str] = None
    sis_import_id: Optional[int] = None
    login_id: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_state: Optional[str] = None
    enrollments: Optional[List[Enrollment]] = None
    email: Optional[str] = None
    locale: Optional[str] = None
    last_login: Optional[datetime] = None
    time_zone: Optional[str] = None
    bio: Optional[str] = None


# ==================== Response Models ====================

class CoursesListResponse(BaseModel):
    """Response for list_courses tool."""

    courses: List[Course]
    total: int


class CourseDetailResponse(BaseModel):
    """Response for get_course tool."""

    course: Course


class CourseUsersResponse(BaseModel):
    """Response for get_course_users tool."""

    users: List[User]
    course_id: int
    total: int


class PreviewHtmlResponse(BaseModel):
    """Response for preview_html tool."""

    html: str
    course_id: int
