# Airtable Tools Documentation

Tools for managing Airtable databases, creating bases, and working with records using the Airtable API.

## Overview

The Airtable tools provide comprehensive database management capabilities for creating, reading, and organizing data in Airtable bases and tables.

## Installation Requirements

- `httpx` (included in main requirements)
- `python-dotenv` (included in main requirements)

## Environment Variables

- `AIRTABLE_PERSONAL_ACCESS_TOKEN` - Required. Personal Access Token from your Airtable account settings

## Available Functions

### Base Management

#### `list_airtable_bases`
Lists all Airtable bases accessible with your API key.

**What it does:**
- Retrieves all bases you have access to
- Shows base names, IDs, and permission levels
- Provides pagination support for large numbers of bases

#### `create_airtable_base`
Creates new Airtable bases with optional initial tables.

**What it does:**
- Creates bases in your default workspace or specified workspace
- Sets up initial table structures during creation
- Configures field types and relationships
- Returns base ID and access information

**Parameters:**
- `name` (required) - Name for the new base
- `workspace_id` (optional) - Target workspace ID
- `tables` (optional) - Initial table configurations

#### `get_base_schema`
Retrieves the complete structure of an Airtable base.

**What it does:**
- Returns all tables, fields, and field types
- Shows table relationships and configurations
- Provides view definitions and metadata

#### `get_base_by_name`
Finds base information using the base name instead of ID.

**What it does:**
- Searches bases by name (case-insensitive)
- Returns base ID and metadata
- Provides helpful error messages with available base names

### Table Management

#### `create_airtable_table`
Creates new tables within existing bases.

**What it does:**
- Adds tables to existing Airtable bases
- Configures field types and properties
- Sets up initial views and relationships

**Parameters:**
- `base_id` (required) - Target base ID
- `table_name` (required) - Name for the new table
- `description` (optional) - Table description
- `fields` (optional) - Field configurations

#### `validate_base_and_table`
Validates that a base and table exist and are accessible.

**What it does:**
- Confirms base and table existence
- Returns available tables if validation fails
- Provides field information for existing tables

### Record Operations

#### `list_records`
Retrieves records from tables with filtering and sorting options.

**What it does:**
- Fetches records with comprehensive filtering
- Supports sorting by multiple fields
- Provides pagination for large datasets
- Uses Airtable formula syntax for complex queries

**Parameters:**
- `base_id` (required) - Base identifier
- `table_name` (required) - Table name
- `fields` (optional) - Specific fields to return
- `filter_formula` (optional) - Airtable filter formula
- `max_records` (optional) - Maximum records to return (max 100)
- `sort` (optional) - Sort field and direction specifications
- `view` (optional) - Named view to use

#### `list_records_by_base_name`
User-friendly version that accepts base names instead of IDs.

**What it does:**
- Same functionality as `list_records`
- Automatically resolves base names to IDs
- Provides more accessible interface for common operations

#### `search_records`
Searches for records by field values with flexible matching.

**What it does:**
- Finds records matching specific field criteria
- Supports exact, partial, and prefix matching
- Returns additional specified fields
- Uses optimized search filters

**Parameters:**
- `base_id` (required) - Base identifier
- `table_name` (required) - Table name
- `search_field` (required) - Field to search in
- `search_value` (required) - Value to search for
- `additional_fields` (optional) - Extra fields to return
- `match_type` (optional) - "exact", "contains", "starts_with"

#### `search_records_by_base_name`
Name-based version of record searching.

#### `get_record_by_id`
Retrieves a specific record using its unique ID.

#### `count_records`
Counts records in a table with optional filtering.

**What it does:**
- Returns record counts for tables
- Supports filtered counting with formulas
- Provides estimates for tables over 100 records

### Template System

#### `create_base_with_template`
Creates bases using predefined templates for common use cases.

**What it does:**
- Implements ready-to-use base structures
- Includes proper field types and relationships
- Provides templates for various business scenarios

**Available Templates:**
- **project_management** - Projects and tasks with status tracking
- **crm** - Contacts, deals, and sales pipeline management
- **inventory** - Product tracking with stock levels and suppliers
- **event_planning** - Events and task management system
- **content_calendar** - Content planning and scheduling workflow

**Parameters:**
- `name` (required) - Base name
- `template` (required) - Template type identifier
- `workspace_id` (optional) - Target workspace

## Field Types Support

Airtable tools support all standard field types:
- **Text**: Single line, multi-line, rich text
- **Numbers**: Integer, decimal, currency, percentage
- **Dates**: Date, date-time, duration
- **Selection**: Single select, multiple select
- **References**: Links to other tables, lookups, rollups
- **Attachments**: Files, images, documents
- **Advanced**: Formula, barcode, rating, checkbox

## Use Cases

- **Data Management**: Organize and structure business data
- **Project Tracking**: Monitor tasks, deadlines, and progress
- **Customer Relationship Management**: Track contacts and interactions
- **Inventory Management**: Monitor stock levels and suppliers
- **Content Planning**: Schedule and organize content creation
- **Event Coordination**: Manage events, attendees, and logistics
- **Research Organization**: Collect and categorize research data

## Authentication

- **Personal Access Tokens**: User-specific API access
- **Scope Control**: Limited to accessible bases and workspaces
- **Permission Levels**: Respects Airtable base permissions

## API Limitations

- **Rate Limits**: 5 requests per second per base
- **Record Limits**: 100 records per API call
- **Base Creation**: May require Team plan or higher
- **Field Types**: Some advanced fields require specific plans

## Error Handling

- **Authentication Errors**: Invalid or missing API tokens
- **Permission Errors**: Insufficient access to bases or tables
- **Validation Errors**: Invalid field types or table structures
- **Rate Limiting**: Automatic handling with appropriate delays