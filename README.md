# Canvas MCP Worker

**Version 2.0** - Restructured for maintainability and comprehensive data responses.

A FastAPI-based HTTP API for Canvas LMS integration, deployed as a Vercel serverless function. Provides student-focused tools that return comprehensive JSON responses for better AI/LLM context.

## 🎯 Key Features

- **Comprehensive JSON Responses**: Returns 40+ fields per course instead of formatted text
- **Modular Architecture**: Easy to extend with new tools
- **Type-Safe**: Full Pydantic validation for requests and responses
- **Auto-Discovery**: Tools are automatically registered via decorators
- **Proper Error Handling**: Detailed Canvas API error messages
- **Student-Focused**: All tools designed for student use cases

## 🚀 Quick Start

### Deploy to Vercel

1. Fork/clone this repository
2. Connect to Vercel
3. Deploy (zero configuration needed)
4. Use the deployed URL in your application

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn main:app --reload

# Test the API
curl http://localhost:8000/tools
```

## 📁 Project Structure

```
canvas-mcp-worker/
├── main.py                      # FastAPI app with routes
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── api/
│   ├── client.py                # Canvas API HTTP client
│   ├── models.py                # Pydantic models for all data types
│   └── exceptions.py            # Custom exception classes
├── tools/
│   ├── base.py                  # BaseTool abstract class
│   ├── registry.py              # Tool auto-discovery system
│   └── courses/                 # Course-related tools
│       ├── list_courses.py      # List all courses
│       ├── get_course.py        # Get single course details
│       ├── get_course_progress.py # Get course progress
│       ├── get_course_users.py  # List course users
│       └── preview_html.py      # Preview HTML content
└── utils/
    └── canvas_params.py         # Helper for building Canvas API params
```

## 🛠️ Available Tools

### Course Tools

| Tool Name | Description | Returns |
|-----------|-------------|---------|
| `list_courses` | List all user's courses | Array of courses with 40+ fields each |
| `get_course` | Get single course details | Complete course object |
| `get_course_progress` | Get student's course progress | Progress tracking data |
| `get_course_users` | List users in course | Array of users/classmates |
| `preview_html` | Preview HTML with course context | Rendered HTML |

## 📡 API Endpoints

### `POST /tools/call`

Execute a Canvas tool.

**Request:**
```json
{
  "tool": "list_courses",
  "args": {
    "enrollmentState": "active",
    "perPage": 100
  },
  "canvasApiUrl": "https://canvas.example.com",
  "canvasApiToken": "your-api-token"
}
```

**Response:**
```json
{
  "result": {
    "courses": [
      {
        "id": 12345,
        "name": "Introduction to Psychology",
        "course_code": "PSY 101",
        "workflow_state": "available",
        "start_at": "2025-01-15T00:00:00Z",
        "end_at": "2025-05-15T23:59:59Z",
        "syllabus_body": "<p>Course syllabus...</p>",
        "term": {
          "id": 1,
          "name": "Spring 2025"
        },
        "enrollments": [
          {
            "type": "StudentEnrollment",
            "computed_current_score": 87.5,
            "computed_current_grade": "B+"
          }
        ],
        "course_progress": {
          "requirement_count": 12,
          "requirement_completed_count": 8
        },
        "permissions": {
          "create_discussion_topic": true
        }
        // ... 30+ more fields
      }
    ],
    "total": 5
  },
  "error": null
}
```

### `GET /tools`

List all available tools with metadata.

### `GET /health`

Health check endpoint.

### `GET /debug/tools/{tool_name}` (Development)

Get detailed information about a specific tool.

### `GET /debug/registry` (Development)

View the complete tool registry.

## 🔧 Adding New Tools

1. Create a new file in `tools/courses/` (or a new category folder)
2. Inherit from `BaseTool`
3. Use the `@register_tool` decorator
4. Implement `execute()` method

**Example:**

```python
from tools.base import BaseTool, ToolContext
from tools.registry import register_tool

@register_tool
class MyNewTool(BaseTool):
    name = "my_new_tool"
    description = "What this tool does"
    category = "courses"

    async def execute(self, ctx: ToolContext) -> dict:
        # Access Canvas API via ctx.client
        data = await ctx.client.get("/some/endpoint")
        return {"data": data}
```

Tools are automatically discovered and registered on import!

## 📊 Data Philosophy

**Old Approach (v1):**
```python
return "Your Active Courses:\n\n• MATH 101: Calculus\n  Course ID: 12345"
```
❌ LLM has to parse text
❌ Missing 95% of available data
❌ No structured information

**New Approach (v2):**
```json
{
  "courses": [{
    "id": 12345,
    "name": "Calculus I",
    "course_code": "MATH 101",
    "workflow_state": "available",
    "syllabus_body": "<p>Full syllabus...</p>",
    "enrollments": [{
      "computed_current_score": 87.5,
      "computed_current_grade": "B+"
    }],
    "course_progress": {
      "requirement_count": 12,
      "requirement_completed_count": 8
    }
    // ... 35+ more fields
  }]
}
```
✅ Structured JSON
✅ Comprehensive data (40+ fields)
✅ LLM can answer complex questions

## 🔐 Security

- API tokens are passed per-request (not stored)
- All Canvas API calls use Bearer token authentication
- Proper error handling prevents token leakage
- CORS enabled for cross-origin requests

## 🐛 Error Handling

The API provides detailed error responses:

```json
{
  "result": null,
  "error": "Canvas API Error [401]: Authentication failed. Invalid or expired Canvas API token."
}
```

Error types:
- **401**: Authentication failed (invalid token)
- **404**: Resource not found
- **400/422**: Validation error (invalid parameters)
- **429**: Rate limit exceeded
- **500+**: Canvas server error

## 📦 Dependencies

- **fastapi**: Modern web framework
- **httpx**: Async HTTP client for Canvas API
- **pydantic**: Data validation and settings
- **python-dateutil**: Date/time parsing

## 🚀 Deployment

### Vercel (Recommended)

1. Connect your Git repository to Vercel
2. Vercel auto-detects the FastAPI app
3. Deploy with zero configuration
4. Get your deployment URL

### Environment Variables (Optional)

```bash
DEFAULT_PER_PAGE=100        # Default pagination size
MAX_PER_PAGE=100            # Maximum pagination size
REQUEST_TIMEOUT=30          # HTTP timeout in seconds
ENABLE_CACHING=false        # Enable response caching
ENABLE_DEBUG=false          # Enable debug logging
```

## 📖 Canvas API Documentation

- [Canvas API Documentation](https://canvas.instructure.com/doc/api/)
- [Courses API](https://canvas.instructure.com/doc/api/courses.html)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tool in `tools/courses/` or create a new category
4. Test locally with `uvicorn main:app --reload`
5. Submit a pull request

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Credits

Built for comprehensive Canvas LMS integration with AI assistants and LLMs.
