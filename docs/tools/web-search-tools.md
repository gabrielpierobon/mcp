# Web Search Tools Documentation

Tools for performing web searches using the Brave Search API.

## Overview

The Web Search tools enable AI agents to search the internet and find information from web pages, news articles, videos, and local businesses.

## Installation Requirements

- `httpx` (included in main requirements)
- `python-dotenv` (included in main requirements)

## Environment Variables

- `BRAVE_API_KEY` - Required. Your Brave Search API subscription token from [api.search.brave.com](https://api.search.brave.com/)

## Available Functions

### `brave_web_search`

Performs comprehensive web searches with pagination and filtering.

**What it does:**
- Searches web pages, news articles, and videos
- Returns combined results from multiple content types
- Supports pagination for large result sets
- Provides filtering and result organization

**Parameters:**
- `query` (required) - Search terms
- `count` (optional) - Results per page (max 20, default 10)
- `offset` (optional) - Pagination offset (max 9, default 0)

**Returns:**
- Combined search results (web, news, videos)
- Total result counts by type
- Search metadata and pagination info

### `brave_local_search`

Searches for local businesses and services with automatic fallback.

**What it does:**
- Finds local businesses, restaurants, services
- Returns location data, contact info, ratings
- Automatically falls back to web search if no local results
- Works with natural language location queries

**Parameters:**
- `query` (required) - Local search terms (e.g., "restaurants near me")
- `count` (optional) - Number of results (max 20, default 10)

**Returns:**
- Local business listings with contact details
- Operating hours, ratings, addresses
- Web search results if no local matches found

## Use Cases

- Research and information gathering
- Content discovery and fact-checking
- Local business and service discovery
- News monitoring and current events
- Competitive research and market analysis

## API Limits

- **Free Tier**: 2,000 queries/month
- **Rate Limit**: 1 query/second
- **Paid Tiers**: Higher limits available

## Error Handling

All functions return status indicators and detailed error messages for:
- Missing or invalid API keys
- Rate limiting issues
- Network connectivity problems
- Invalid search parameters