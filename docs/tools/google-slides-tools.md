# Google Slides Tools Documentation

Tools for creating, editing, and managing Google Presentations using the Google Slides API with OAuth2 authentication.

## Overview

The Google Slides tools provide comprehensive presentation management capabilities including slide creation, content addition, and template-based workflows.

## Installation Requirements

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Environment Variables

- `GOOGLE_CREDENTIALS_FILE` (optional) - Path to OAuth2 credentials JSON file (default: "credentials.json")
- `GOOGLE_TOKEN_FILE` (optional) - Path to store OAuth2 token (default: "token.json")

## Authentication Setup

1. **Google Cloud Console**: Create project and enable Google Slides API
2. **OAuth2 Credentials**: Download credentials.json file
3. **First-time Setup**: Tools will open browser for permission grant
4. **Token Storage**: Subsequent uses are automatic

## Available Functions

### Presentation Creation

#### `create_google_slides`
Creates new Google Presentations with template and sharing options.

**What it does:**
- Creates presentations with custom titles
- Optionally copies from existing template presentations
- Automatically shares with specified email addresses
- Returns presentation URLs and access information

**Parameters:**
- `title` (required) - Presentation title
- `template_id` (optional) - Template presentation ID to copy from
- `share_with` (optional) - Email addresses for sharing

### Slide Management

#### `add_slide`
Adds new slides to presentations with specific layouts.

**What it does:**
- Creates slides with predefined layout types
- Supports various slide layouts and structures
- Allows insertion at specific positions
- Returns slide IDs for further operations

**Parameters:**
- `presentation_id` (required) - Target presentation ID
- `slide_layout` (optional) - Layout type (default: "BLANK")
- `title` (optional) - Slide title for reference
- `insert_index` (optional) - Position to insert slide

#### `create_slide_with_content`
Creates slides and populates placeholders in one operation.

**What it does:**
- Combines slide creation with content addition
- Automatically fills title and body placeholders
- Uses appropriate layouts for content types
- Provides comprehensive slide setup

**Parameters:**
- `presentation_id` (required) - Target presentation ID
- `slide_layout` (optional) - Layout type (default: "TITLE_AND_BODY")
- `title` (optional) - Title content for slide
- `body_content` (optional) - Body content for slide
- `insert_index` (optional) - Position to insert slide

#### `add_slide_to_last_presentation`
Adds slides with content to the most recently created presentation.

**What it does:**
- Uses session memory to identify recent presentations
- Creates and populates slides automatically
- Simplifies workflow for sequential slide creation

**Parameters:**
- `slide_layout` (optional) - Layout type (default: "TITLE_AND_BODY")
- `title` (optional) - Slide title
- `body_content` (optional) - Slide body content

### Content Addition

#### `add_content_to_slide_placeholders`
Fills existing placeholders in slides with content.

**What it does:**
- Locates title and body placeholders in slides
- Fills placeholders with specified text content
- Handles different placeholder types automatically
- Returns information about filled placeholders

**Parameters:**
- `presentation_id` (required) - Target presentation ID
- `slide_id` (required) - Target slide ID
- `title_text` (optional) - Text for title placeholder
- `body_text` (optional) - Text for body placeholder

#### `add_text_to_slide`
Adds custom text boxes to slides with positioning control.

**What it does:**
- Creates text boxes at specified coordinates
- Allows custom positioning and sizing
- Supports custom text formatting
- Provides precise layout control

**Parameters:**
- `presentation_id` (required) - Target presentation ID
- `slide_id` (required) - Target slide ID
- `text` (required) - Text content to add
- `x` (optional) - X coordinate in points (default: 100)
- `y` (optional) - Y coordinate in points (default: 100)
- `width` (optional) - Text box width in points (default: 400)
- `height` (optional) - Text box height in points (default: 100)

### Utility Functions

#### `get_slide_info`
Provides detailed information about slide structure and elements.

**What it does:**
- Analyzes slide layout and placeholder types
- Lists all slide elements and their properties
- Identifies available placeholders for content
- Returns structural information for planning

**Parameters:**
- `presentation_id` (required) - Target presentation ID
- `slide_id` (required) - Target slide ID

### Context Management

#### `list_recent_presentations`
Lists recently created presentations from current session.

**What it does:**
- Shows presentations created during current session
- Provides titles, IDs, URLs, and slide counts
- Helps identify available presentations for operations

#### `find_presentation_by_title`
Searches for presentations by title within session context.

**What it does:**
- Case-insensitive title searching
- Returns matching presentation information
- Shows all available titles if no matches found

## Slide Layouts

Available layout types:
- **BLANK** - Empty slide for custom content
- **TITLE_AND_BODY** - Standard title with body content area
- **TITLE_ONLY** - Title-only slide for section headers
- **SECTION_HEADER** - Section divider slide
- **TWO_COLUMNS_TEXT** - Two-column text layout
- **TWO_COLUMNS_TEXT_AND_IMAGE** - Mixed text and image columns
- **TITLE_AND_TWO_COLUMNS** - Title with two-column content
- **ONE_COLUMN_TEXT** - Single column text layout
- **MAIN_POINT** - Emphasis slide for key points
- **BIG_NUMBER** - Large number or statistic display

## Session Context Features

The Google Slides tools maintain session memory for:
- **Recent Presentations**: Track created presentations
- **Slide Management**: Remember slide IDs and structures
- **Quick Operations**: Enable "last created" functionality
- **Template Tracking**: Monitor template usage

## Placeholder Types

Supported placeholder types:
- **TITLE** - Main slide titles
- **SUBTITLE** - Secondary titles and subtitles
- **BODY** - Main content areas
- **CENTERED_TITLE** - Centered title placeholders
- **SLIDE_NUMBER** - Automatic slide numbering

## Use Cases

- **Business Presentations**: Sales decks, project updates, reports
- **Educational Content**: Lectures, training materials, workshops
- **Marketing Materials**: Product launches, company overviews
- **Meeting Presentations**: Status updates, proposals, reviews
- **Conference Materials**: Speaking presentations, workshop slides
- **Template Creation**: Reusable presentation frameworks

## Integration Patterns

- **With Web Search**: Create presentations from research results
- **With Airtable**: Generate slides from database content
- **With Google Sheets**: Reference data in presentation slides
- **With Weather Data**: Create weather briefing presentations
- **With Web Crawling**: Present website analysis results

## Content Features

- **Text Content**: Title and body text management
- **Layout Control**: Predefined and custom layouts
- **Positioning**: Precise element placement
- **Template Support**: Copy from existing presentations
- **Collaborative Sharing**: Multi-user access and editing

## Error Handling

- **Authentication Failures**: OAuth2 token refresh and re-authorization
- **Permission Errors**: Insufficient access to presentations
- **Layout Errors**: Invalid slide layouts or positioning
- **Content Errors**: Placeholder filling failures
- **Network Issues**: Connection timeouts and API failures

## API Quotas

- **Read Requests**: 100 requests per 100 seconds per user
- **Write Requests**: 100 requests per 100 seconds per user
- **Daily Limit**: 50,000 requests per day per project
- **Presentation Size**: Limited by Google Slides size restrictions

## Best Practices

- **Layout Selection**: Choose appropriate layouts for content types
- **Content Planning**: Prepare content before slide creation
- **Session Efficiency**: Use context features for workflow optimization
- **Template Management**: Create reusable templates for consistency
- **Collaboration Setup**: Configure sharing and permissions appropriately