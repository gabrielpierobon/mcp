# Google Sheets Tools Documentation

Tools for creating, editing, and managing Google Spreadsheets using the Google Sheets API with OAuth2 authentication.

## Overview

The Google Sheets tools provide comprehensive spreadsheet management capabilities including creation, data manipulation, and collaborative features.

## Installation Requirements

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Environment Variables

- `GOOGLE_CREDENTIALS_FILE` (optional) - Path to OAuth2 credentials JSON file (default: "credentials.json")
- `GOOGLE_TOKEN_FILE` (optional) - Path to store OAuth2 token (default: "token.json")

## Authentication Setup

1. **Google Cloud Console**: Create project and enable Google Sheets API
2. **OAuth2 Credentials**: Download credentials.json file
3. **First-time Setup**: Tools will open browser for permission grant
4. **Token Storage**: Subsequent uses are automatic

## Available Functions

### Spreadsheet Creation

#### `create_google_sheet`
Creates new Google Spreadsheets with multiple sheets and sharing options.

**What it does:**
- Creates spreadsheets with custom titles
- Sets up multiple sheets with specified names
- Automatically shares with specified email addresses
- Returns spreadsheet URLs and access information

**Parameters:**
- `title` (required) - Spreadsheet title
- `sheet_names` (optional) - List of sheet names to create (default: ["Sheet1"])
- `share_with` (optional) - Email addresses for sharing

### Data Operations

#### `write_to_sheet`
Writes data to specific ranges in spreadsheets.

**What it does:**
- Writes 2D arrays of data to specified cell ranges
- Uses A1 notation for range specification
- Supports different value input options
- Returns update statistics and confirmation

**Parameters:**
- `spreadsheet_id` (required) - Target spreadsheet ID
- `range_name` (required) - A1 notation range (e.g., "Sheet1!A1:C3")
- `values` (required) - 2D array of cell values
- `value_input_option` (optional) - "RAW" or "USER_ENTERED" (default: "USER_ENTERED")

#### `read_from_sheet`
Reads data from spreadsheet ranges.

**What it does:**
- Extracts data from specified cell ranges
- Returns data as 2D arrays
- Provides row and column count information
- Handles empty cells and missing data

**Parameters:**
- `spreadsheet_id` (required) - Source spreadsheet ID
- `range_name` (required) - A1 notation range to read

#### `clear_sheet_range`
Clears data from specified ranges.

**What it does:**
- Removes data from specific cell ranges
- Preserves formatting and sheet structure
- Returns confirmation of cleared ranges

### Context-Aware Operations

#### `append_to_last_sheet`
Appends data to the most recently created spreadsheet.

**What it does:**
- Uses session memory to track recent spreadsheets
- Automatically finds next available row
- Appends data without overwriting existing content
- Calculates optimal range for new data

**Parameters:**
- `values` (required) - 2D array of data to append
- `start_row` (optional) - Specific starting row (auto-calculated if not provided)
- `sheet_name` (optional) - Target sheet name (uses default if not provided)

#### `append_to_sheet_by_title`
Appends data to spreadsheets found by title search.

**What it does:**
- Searches recent spreadsheets by title
- Supports partial title matching
- Automatically handles data placement
- Provides context information for successful operations

**Parameters:**
- `title_search` (required) - Partial title to search for
- `values` (required) - Data to append
- `start_row` (optional) - Starting row specification
- `sheet_name` (optional) - Target sheet name

### Context Management

#### `list_recent_spreadsheets`
Lists recently created spreadsheets from current session.

**What it does:**
- Shows spreadsheets created during current session
- Provides titles, IDs, URLs, and sheet names
- Helps identify available spreadsheets for operations

#### `find_spreadsheet_by_title`
Searches for spreadsheets by title within session context.

**What it does:**
- Case-insensitive title searching
- Returns matching spreadsheet information
- Shows all available titles if no matches found

## Session Context Features

The Google Sheets tools maintain session memory for:
- **Recent Spreadsheets**: Track created spreadsheets
- **Default Sheets**: Remember primary sheet names
- **Quick Operations**: Enable "last created" functionality
- **Title Search**: Find spreadsheets without IDs

## Supported Data Types

- **Text**: String values and formatted text
- **Numbers**: Integers, decimals, percentages
- **Dates**: Date values and date-time combinations
- **Formulas**: Excel-style formulas and functions
- **Boolean**: TRUE/FALSE values
- **Empty Cells**: Null or empty string values

## Sharing and Permissions

- **Email Sharing**: Automatic sharing during creation
- **Permission Levels**: Reader, commenter, editor access
- **Notification Control**: Optional email notifications
- **Bulk Sharing**: Share with multiple users simultaneously

## Use Cases

- **Data Collection**: Gathering and organizing information
- **Reporting**: Creating structured reports and dashboards
- **Collaboration**: Shared data entry and analysis
- **Data Export**: Moving data from other systems
- **Project Management**: Tracking tasks, timelines, and resources
- **Financial Planning**: Budgets, forecasts, and calculations
- **Research Organization**: Survey results and study data

## Integration Patterns

- **With Web Search**: Store search results in organized format
- **With Weather Data**: Create weather tracking logs
- **With Airtable**: Export/import data between platforms
- **With Calculator**: Store computation results
- **With Web Crawling**: Organize extracted website data

## Range Notation

Uses Google Sheets A1 notation:
- **Single Cell**: "A1", "B5"
- **Range**: "A1:C3", "B2:D10"
- **Entire Column**: "A:A", "B:C"
- **Entire Row**: "1:1", "5:10"
- **Sheet Specific**: "Sheet1!A1:B5"

## Error Handling

- **Authentication Failures**: OAuth2 token refresh and re-authorization
- **Permission Errors**: Insufficient access to spreadsheets
- **Range Errors**: Invalid A1 notation or out-of-bounds ranges
- **Network Issues**: Connection timeouts and API failures
- **Quota Limits**: Google API usage limits and rate limiting

## API Quotas

- **Read Requests**: 100 requests per 100 seconds per user
- **Write Requests**: 100 requests per 100 seconds per user
- **Daily Limit**: 50,000 requests per day per project
- **Concurrent Requests**: Limited concurrent operations

## Best Practices

- **Batch Operations**: Group multiple writes for efficiency
- **Range Optimization**: Use appropriate range sizes
- **Session Management**: Leverage context for workflow efficiency
- **Error Recovery**: Implement retry logic for network issues
- **Permission Verification**: Check access before operations