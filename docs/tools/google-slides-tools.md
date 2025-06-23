# Google Slides Tools Documentation

Comprehensive documentation for Google Slides presentation management and creation tools with **🆕 Enhanced Design Capabilities**.

## Tool Overview

The Google Slides tools provide complete presentation management with advanced design features:
- **Presentation Creation**: Create new presentations with templates
- **Slide Management**: Add, configure, and organize slides
- **Content Management**: Add and style text with placeholders and custom text boxes
- **🆕 Design Enhancement**: Background colors, font styling, and advanced layout control
- **Collaboration**: Share presentations with team members
- **Context Awareness**: Track recent presentations for easy access

## Available Tools

| Tool | Function | Purpose |
|------|----------|---------|
| `create_google_slides` | Create new presentation | Initialize presentations with optional templates |
| `add_slide` | Add slide with layout | Create slides with predefined layouts |
| `create_slide_with_content` | Add slide with content | **Recommended** - Create and populate slides in one step |
| `add_content_to_slide_placeholders` | Fill placeholders | Add content to title/body placeholders |
| `add_text_to_slide` | Custom text box | Add positioned text boxes |
| **🆕 `change_slide_background`** | **Background colors/images** | **Change slide backgrounds with colors or images** |
| **🆕 `add_styled_text_box`** | **Styled text boxes** | **Add text boxes with font, color, and background styling** |
| **🆕 `update_text_style`** | **Update text styling** | **Modify existing text box fonts, colors, and formatting** |
| **🆕 `add_multiple_text_boxes`** | **Batch text boxes** | **Add multiple styled text boxes efficiently** |
| `add_slide_to_last_presentation` | Quick slide addition | Add slides to most recent presentation |
| `get_slide_info` | Slide analysis | Get slide structure and element information |
| `list_recent_presentations` | Context query | List recently created presentations |
| `find_presentation_by_title` | Find presentations | Search presentations by title |

## 🆕 Enhanced Design Capabilities

### Background Customization

**Change slide backgrounds with colors or images:**

```python
# Solid color background
await change_slide_background(
    presentation_id="presentation_id",
    slide_id="slide_id",
    background_type="color",
    color_hex="#1e3a8a"  # Deep blue
)

# Image background
await change_slide_background(
    presentation_id="presentation_id", 
    slide_id="slide_id",
    background_type="image",
    image_url="https://example.com/background.jpg"
)
```

**Supported Colors:**
- Hex format: `#FF5733`, `#3498DB`, `#2ECC71`
- Popular colors: `#1e3a8a` (blue), `#dc2626` (red), `#059669` (green)

### Advanced Text Styling

**Create styled text boxes with comprehensive formatting:**

```python
await add_styled_text_box(
    presentation_id="presentation_id",
    slide_id="slide_id", 
    text="Revolutionary MCP Server",
    x=100, y=150,
    width=600, height=80,
    font_family="Arial",
    font_size=32,
    font_color="#FFFFFF",
    background_color="#1e3a8a",
    bold=True,
    alignment="CENTER"
)
```

**Styling Options:**
- **Font Families**: "Arial", "Times New Roman", "Calibri", "Helvetica", "Georgia"
- **Font Sizes**: Any point size (e.g., 12, 18, 24, 32, 48)
- **Colors**: Hex format for text and background colors
- **Text Formatting**: Bold, italic support
- **Alignment**: "LEFT", "CENTER", "RIGHT", "JUSTIFIED"

### Batch Text Box Creation

**Add multiple styled text boxes efficiently:**

```python
text_boxes = [
    {
        "text": "🚀 Revolutionary Features",
        "x": 50, "y": 100, "width": 300, "height": 60,
        "font_family": "Arial", "font_size": 24,
        "font_color": "#FFFFFF", "background_color": "#dc2626",
        "bold": True, "alignment": "CENTER"
    },
    {
        "text": "68+ comprehensive tools for AI agents",
        "x": 50, "y": 180, "width": 400, "height": 40,
        "font_family": "Calibri", "font_size": 16,
        "font_color": "#2d3748", "italic": True
    }
]

await add_multiple_text_boxes(
    presentation_id="presentation_id",
    slide_id="slide_id",
    text_boxes=text_boxes
)
```

### Text Style Updates

**Modify existing text boxes:**

```python
await update_text_style(
    presentation_id="presentation_id",
    text_box_id="textbox_id",
    font_family="Georgia",
    font_size=20,
    font_color="#2d3748",
    bold=False,
    alignment="CENTER"
)
```

## Core Slide Layouts

Available layouts for slides:
- **BLANK**: Empty slide for custom design
- **TITLE_AND_BODY**: Title and bullet point content (most common)
- **TITLE_ONLY**: Title-only slide
- **SECTION_HEADER**: Section divider slide
- **TWO_COLUMNS_TEXT**: Two-column text layout
- **TWO_COLUMNS_TEXT_AND_IMAGE**: Text and image columns
- **TITLE_AND_TWO_COLUMNS**: Title with two-column content
- **ONE_COLUMN_TEXT**: Single column text
- **MAIN_POINT**: Highlight slide for key points
- **BIG_NUMBER**: Large number or statistic display

## Setup Requirements

### Installation

```bash
# Install Google API dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Authentication Setup

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project or select existing one

2. **Enable APIs**:
   - Enable Google Slides API
   - Enable Google Drive API

3. **Create Credentials**:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Desktop application" 
   - Download JSON file as `credentials.json`

4. **Environment Configuration**:
```env
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

### First Run Authorization

The first time you use Google Slides tools:
1. A browser window will open for OAuth authorization
2. Sign in with your Google account
3. Grant permissions for Slides and Drive access
4. Token will be saved automatically for future use

## Design Best Practices

### Color Schemes

**Professional Business:**
- Background: `#f8fafc` (light gray)
- Headers: `#1e293b` (dark slate)
- Accent: `#3b82f6` (blue)
- Text: `#374151` (gray)

**Modern Tech:**
- Background: `#0f172a` (dark blue)
- Headers: `#ffffff` (white)
- Accent: `#06b6d4` (cyan)
- Text: `#e2e8f0` (light gray)

**Vibrant Creative:**
- Background: `#fef3c7` (light yellow)
- Headers: `#dc2626` (red)
- Accent: `#059669` (green)
- Text: `#1f2937` (dark gray)

### Typography Guidelines

**Font Combinations:**
- **Professional**: Arial + Calibri
- **Academic**: Times New Roman + Georgia
- **Modern**: Helvetica + Helvetica Neue
- **Clean**: Calibri + Segoe UI

**Size Hierarchy:**
- **Main Title**: 36-48pt, Bold
- **Section Headers**: 24-32pt, Bold
- **Body Text**: 16-20pt, Regular
- **Captions**: 12-14pt, Italic

### Layout Positioning

**Standard Coordinates (720p slide = 960x540pt):**
- **Title Area**: x=50, y=50, width=860, height=80
- **Content Area**: x=50, y=150, width=860, height=300
- **Footer Area**: x=50, y=480, width=860, height=40

**Multi-Column Layouts:**
- **Left Column**: x=50, width=400
- **Right Column**: x=480, width=430
- **Three Columns**: x=50/340/630, width=270 each

## Common Workflows

### Professional Presentation Creation

1. **Create Base Presentation**:
```python
presentation = await create_google_slides(
    title="MCP Server Overview",
    share_with=["team@company.com"]
)
```

2. **Add Title Slide with Background**:
```python
# Change background color
await change_slide_background(
    presentation_id=presentation["presentation_id"],
    slide_id="slide_id",
    background_type="color", 
    color_hex="#1e3a8a"
)

# Add styled title
await add_styled_text_box(
    presentation_id=presentation["presentation_id"],
    slide_id="slide_id",
    text="Revolutionary MCP Server",
    x=100, y=200, width=760, height=100,
    font_family="Arial", font_size=48,
    font_color="#FFFFFF", bold=True,
    alignment="CENTER"
)
```

3. **Add Content Slides**:
```python
await create_slide_with_content(
    presentation_id=presentation["presentation_id"],
    slide_layout="TITLE_AND_BODY",
    title="Key Features",
    body_content="• 68+ comprehensive tools\n• Visual context with screen capture\n• Secure file operations"
)
```

### Quick Slide Enhancement

**Transform a basic slide into a visually appealing one:**

```python
# Get slide information
slide_info = await get_slide_info(presentation_id, slide_id)

# Change background
await change_slide_background(
    presentation_id, slide_id,
    background_type="color",
    color_hex="#f1f5f9"  # Light gray
)

# Add multiple styled elements
text_boxes = [
    {
        "text": "🚀 Key Feature",
        "x": 50, "y": 100, "width": 200, "height": 50,
        "font_size": 24, "font_color": "#1e40af", "bold": True
    },
    {
        "text": "Detailed explanation of the revolutionary capability",
        "x": 50, "y": 160, "width": 600, "height": 100,
        "font_size": 16, "font_color": "#374151"
    }
]

await add_multiple_text_boxes(presentation_id, slide_id, text_boxes)
```

### Template-Based Workflow

**Create consistent presentation styling:**

```python
# Define standard styling template
title_style = {
    "font_family": "Arial",
    "font_size": 32,
    "font_color": "#1e293b", 
    "bold": True,
    "alignment": "CENTER"
}

content_style = {
    "font_family": "Calibri",
    "font_size": 18,
    "font_color": "#374151",
    "background_color": "#f8fafc"
}

# Apply to multiple slides
for slide_data in presentation_content:
    slide = await create_slide_with_content(
        presentation_id=presentation_id,
        slide_layout="BLANK"
    )
    
    await change_slide_background(
        presentation_id, slide["slide_id"],
        background_type="color", color_hex="#ffffff"
    )
    
    await add_styled_text_box(
        presentation_id, slide["slide_id"],
        text=slide_data["title"],
        x=50, y=50, width=860, height=80,
        **title_style
    )
```

## Error Handling

**Common Issues and Solutions:**

1. **Authentication Errors**:
   - Ensure `credentials.json` is in correct location
   - Check that Google Slides API is enabled
   - Re-run OAuth flow if token expires

2. **Color Format Errors**:
   - Use valid hex format: `#RRGGBB`
   - Include the `#` symbol
   - Use 6-character hex codes

3. **Font Issues**:
   - Use standard font names
   - Check font availability in Google Slides
   - Fall back to system fonts if custom fonts fail

4. **Layout Problems**:
   - Ensure coordinates are within slide bounds
   - Check that width/height values are positive
   - Verify slide exists before adding elements

## Session Context Features

**Recent Presentation Tracking:**
- Automatically tracks recently created presentations
- Enables quick access with `add_slide_to_last_presentation`
- Search presentations by title
- Maintains session memory for workflow continuity

**Context Query Examples:**
```python
# List recent presentations
recent = await list_recent_presentations()

# Find specific presentation
found = await find_presentation_by_title("MCP Server")

# Add to most recent presentation
await add_slide_to_last_presentation(
    slide_layout="TITLE_AND_BODY",
    title="New Feature",
    body_content="Enhanced capabilities"
)
```

## Integration Examples

### With File System Tools

```python
# Read content from local files
content = await read_file("presentation_outline.txt")

# Create slides from file content
lines = content["content"].split("\n")
for line in lines:
    if line.startswith("# "):
        await create_slide_with_content(
            presentation_id=presentation_id,
            title=line[2:],
            slide_layout="TITLE_ONLY"
        )
```

### With Web Search Tools

```python
# Search for relevant information
search_results = await brave_web_search("AI agent capabilities")

# Create slide with search insights
await create_slide_with_content(
    presentation_id=presentation_id,
    title="Industry Insights",
    body_content=f"• {search_results['results'][0]['title']}\n• Latest trends in AI automation"
)
```

### With Screen Capture

```python
# Capture current screen for context
await quick_capture("Current presentation work")

# Add visual context to slides
await add_styled_text_box(
    presentation_id, slide_id,
    text="📸 Visual context captured for reference",
    x=50, y=400, width=400, height=40,
    font_size=14, font_color="#6b7280", italic=True
)
```

## Advanced Features

### Custom Positioning System

**Precise element placement:**
```python
# Create grid-based layout
grid_items = [
    {"text": "Feature 1", "x": 50, "y": 150},
    {"text": "Feature 2", "x": 350, "y": 150},
    {"text": "Feature 3", "x": 650, "y": 150},
    {"text": "Feature 4", "x": 50, "y": 300},
    {"text": "Feature 5", "x": 350, "y": 300},
    {"text": "Feature 6", "x": 650, "y": 300}
]

for item in grid_items:
    await add_styled_text_box(
        presentation_id, slide_id,
        text=item["text"],
        x=item["x"], y=item["y"],
        width=250, height=100,
        font_size=16, alignment="CENTER",
        background_color="#e5e7eb"
    )
```

### Conditional Styling

**Dynamic styling based on content:**
```python
def get_style_for_priority(priority):
    styles = {
        "high": {"background_color": "#dc2626", "font_color": "#ffffff"},
        "medium": {"background_color": "#f59e0b", "font_color": "#ffffff"},
        "low": {"background_color": "#10b981", "font_color": "#ffffff"}
    }
    return styles.get(priority, styles["medium"])

# Apply conditional styling
for feature in features:
    style = get_style_for_priority(feature["priority"])
    await add_styled_text_box(
        presentation_id, slide_id,
        text=feature["name"],
        **style
    )
```

## Performance Optimization

**Batch Operations:**
- Use `add_multiple_text_boxes` for multiple elements
- Combine styling operations when possible
- Minimize API calls by batching requests

**Efficient Workflows:**
- Create presentations with sharing enabled
- Use session context for related operations
- Cache presentation IDs for repeated access

---

*Enhanced with revolutionary design capabilities including background colors, advanced text styling, and efficient batch operations for professional presentation creation.*