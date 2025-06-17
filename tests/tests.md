# MCP Server Test Suite

A comprehensive test suite for the Model Context Protocol (MCP) server using pytest. This test suite ensures the reliability and functionality of all tools and server components with proper mocking of external dependencies.

## 🏗️ Test Architecture

### Test Categories

**🔧 Unit Tests**
- Individual tool testing with mocked dependencies
- Parameter validation and error handling
- Response format consistency
- Edge cases and boundary conditions

**🔗 Integration Tests**
- Server initialization and startup
- Tool registration process
- Cross-tool compatibility
- End-to-end workflows

**📊 Coverage Areas**
- ✅ Calculator Tool (arithmetic operations)
- ✅ Weather Tool (Open-Meteo API, mocked)
- ✅ Brave Search (web/local search, mocked)
- ✅ File System Tool (read, list, search operations)
- ✅ File Writing Tool (sandbox security, file operations)
- ✅ Screen Capture Tool (cross-platform capture, mocked)
- ✅ Airtable Tool (database operations, mocked) - 31 tests
- ✅ Web Crawling Tool (Crawl4AI, mocked) - 21 tests
- ✅ Browser Automation Tool (Playwright, mocked) - 54 tests
- ✅ Google Workspace Tools (Sheets, Docs, Slides, mocked) - 80 tests
- ✅ RAG Knowledge Base (vector operations, mocked) - 35 tests
- ✅ Launcher Scripts (server startup, configuration, mocked) - 41 tests

> **Note:** The test suite is designed to be run directly with `pytest`. No custom runner script is required.

> **Note:** If you encounter `ModuleNotFoundError: No module named 'fastmcp'` or issues with real API calls, ensure all external dependencies are properly mocked and your PYTHONPATH includes the project root.

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies (example)
pip install pytest pytest-cov pytest-xdist
# Add any other dependencies your tests require
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test files
pytest tests/test_calculator_tool.py -v
pytest tests/test_weather_tool.py -v
pytest tests/test_brave_search.py -v
pytest tests/test_launcher_scripts.py -v

# Run specific test categories with markers
pytest tests/ -m "unit" -v               # Unit tests only  
pytest tests/ -m "integration" -v        # Integration tests only
pytest tests/ -m "not slow" -v           # Skip slow tests

# Verbose output with detailed assertions
pytest tests/ -v -s

# Parallel execution (requires pytest-xdist)
pytest tests/ -n auto
```

### Test Structure

```
tests/
├── 📄 conftest.py              # Shared fixtures and configuration
├── 📄 pytest.ini              # Pytest configuration
├── 📄 README.md               # This file
│
├── 🔧 Unit Tests
│   ├── test_calculator_tool.py      # ✅ Calculator operations
│   ├── test_brave_search.py         # ✅ Web search (mocked)
│   ├── test_weather_tool.py         # ✅ Weather API (mocked)
│   ├── test_file_system_tool.py     # ✅ File operations
│   ├── test_file_writing_tool.py    # ✅ File writing & security
│   ├── test_screen_capture_tool.py  # ✅ Screen capture (mocked)
│   ├── test_airtable_tool.py        # ✅ Database operations
│   ├── test_crawl4ai_tool.py        # ✅ Web crawling
│   ├── test_playwright_browser_tool.py # ✅ Browser automation
│   ├── test_google_sheets_tool.py   # ✅ Google Sheets
│   ├── test_google_docs_tool.py     # ✅ Google Docs
│   ├── test_google_slides_tool.py   # ✅ Google Slides
│   ├── test_rag_tool.py             # ✅ Knowledge base
│   └── test_launcher_scripts.py     # ✅ Server launchers
│
└── 🔗 Integration Tests
    └── test_server_integration.py   # ✅ Server-level testing
```

## 🎯 Test Philosophy

### Mocking Strategy
- **External APIs**: All HTTP calls mocked with realistic responses
- **File System**: Isolated temporary directories for file operations
- **Screen Capture**: Mocked image generation and clipboard operations
- **Database Operations**: Mocked connections and responses
- **Browser Automation**: Mocked browser instances and page interactions

### Error Handling
- Network failures
- API rate limits
- Permission denied
- Invalid parameters
- Missing dependencies
- Timeout scenarios

### Security Testing
- Path traversal prevention
- Sandbox enforcement
- API key protection
- Input validation

## 📋 Test Examples

### Running Calculator Tests
```bash
# Test basic arithmetic
pytest tests/test_calculator_tool.py -v

# Expected output:
# ✅ test_addition_success
# ✅ test_subtraction_success  
# ✅ test_multiplication_success
# ✅ test_division_success
# ✅ test_division_by_zero_error
# ✅ test_invalid_operation_error
```

### Running Weather Tests
```bash
# Test weather API (mocked)
pytest tests/test_weather_tool.py -v

# Expected output:
# ✅ test_get_weather_success_default_location
# ✅ test_get_weather_success_custom_location
# ✅ test_get_weather_geocoding_failure
# ✅ test_get_weather_api_error
# ✅ test_get_weather_network_error
```

### Running File System Tests
```bash
# Test file operations
pytest tests/test_file_system_tool.py -v

# Expected output:
# ✅ test_read_file_success
# ✅ test_list_directory_success
# ✅ test_search_files_by_name
# ✅ test_path_validation_security
# ✅ test_binary_file_handling
```

### Running Airtable Tests
```bash
# Test Airtable database operations (mocked)
pytest tests/test_airtable_tool.py -v

# Expected output:
# ✅ test_create_airtable_base_success
# ✅ test_create_base_with_template_project_management
# ✅ test_list_records_success
# ✅ test_search_records_exact_match
# ✅ test_get_base_by_name_success
# ✅ test_validate_base_and_table_success
# ✅ test_error_handling_scenarios
# ... (31 total tests covering all functions)
```

### Running Web Crawling Tests
```bash
# Test Crawl4AI web crawling tool (mocked)
pytest tests/test_crawl4ai_tool.py -v

# Expected output:
# ✅ test_crawl_webpage_success_markdown
# ✅ test_crawl_webpage_success_html
# ✅ test_crawl_webpage_success_text
# ✅ test_crawl_webpage_success_all_formats
# ✅ test_crawl_webpage_with_custom_parameters
# ✅ test_crawl_webpage_crawl4ai_unavailable
# ✅ test_crawl_webpage_crawler_failure
# ✅ test_crawl_webpage_exception_handling
# ✅ test_crawl_multiple_webpages_success
# ✅ test_crawl_multiple_webpages_crawl4ai_unavailable
# ✅ test_crawl_multiple_webpages_custom_parameters
# ✅ test_extract_structured_data_success
# ✅ test_extract_structured_data_crawl4ai_unavailable
# ✅ test_normalize_unicode
# ✅ test_clean_text_for_json
# ✅ test_clean_dict_for_json
# ✅ test_get_browser_config_with_defaults
# ✅ test_get_browser_config_unavailable
# ✅ test_tool_registration_available
# ✅ test_tool_registration_unavailable
# ✅ test_timeout_handling
# ... (21 total tests covering all web crawling functions)
```

### Running Browser Automation Tests
```bash
# Test Playwright browser automation tool (mocked)
pytest tests/test_playwright_browser_tool.py -v

# Expected output:
# ✅ test_launch_browser_success_chromium
# ✅ test_launch_browser_success_firefox
# ✅ test_launch_browser_success_webkit
# ✅ test_launch_browser_existing_context
# ✅ test_launch_browser_playwright_unavailable
# ✅ test_launch_browser_exception_handling
# ✅ test_navigate_to_page_success
# ✅ test_navigate_to_page_auto_launch
# ✅ test_navigate_to_page_custom_parameters
# ✅ test_navigate_to_page_playwright_unavailable
# ✅ test_navigate_to_page_exception_handling
# ✅ test_get_page_content_text
# ✅ test_get_page_content_html
# ✅ test_get_page_content_markdown
# ✅ test_get_page_content_screenshot
# ✅ test_get_page_content_with_selector
# ✅ test_get_page_content_no_active_page
# ✅ test_get_page_content_playwright_unavailable
# ✅ test_click_element_success
# ✅ test_click_element_with_navigation
# ✅ test_click_element_no_active_page
# ✅ test_click_element_playwright_unavailable
# ✅ test_click_element_exception_handling
# ✅ test_fill_form_field_success
# ✅ test_fill_form_field_no_clear
# ✅ test_fill_form_field_no_active_page
# ✅ test_fill_form_field_playwright_unavailable
# ✅ test_fill_form_field_exception_handling
# ✅ test_wait_for_element_success
# ✅ test_wait_for_element_custom_state
# ✅ test_wait_for_element_no_active_page
# ✅ test_wait_for_element_playwright_unavailable
# ✅ test_wait_for_element_exception_handling
# ✅ test_execute_javascript_success
# ✅ test_execute_javascript_complex_script
# ✅ test_execute_javascript_no_active_page
# ✅ test_execute_javascript_playwright_unavailable
# ✅ test_execute_javascript_exception_handling
# ✅ test_get_accessibility_snapshot_success
# ✅ test_get_accessibility_snapshot_all_elements
# ✅ test_get_accessibility_snapshot_no_active_page
# ✅ test_get_accessibility_snapshot_playwright_unavailable
# ✅ test_get_accessibility_snapshot_exception_handling
# ✅ test_close_browser_context_success
# ✅ test_close_browser_context_not_found
# ✅ test_close_browser_context_playwright_unavailable
# ✅ test_close_browser_context_exception_handling
# ✅ test_list_browser_contexts_empty
# ✅ test_list_browser_contexts_with_contexts
# ✅ test_list_browser_contexts_mixed_states
# ✅ test_tool_registration_available
# ✅ test_tool_registration_unavailable
# ✅ test_complex_workflow_success
# ✅ test_context_isolation
# ... (54 total tests covering all browser automation functions)
```

### Running Google Workspace Tests
```bash
# Test Google Sheets operations (mocked)
pytest tests/test_google_sheets_tool.py -v

# Expected output:
# ✅ test_create_google_sheet_success
# ✅ test_create_google_sheet_with_custom_sheets
# ✅ test_create_google_sheet_with_sharing
# ✅ test_create_google_sheet_apis_unavailable
# ✅ test_write_to_sheet_success
# ✅ test_write_to_sheet_raw_input
# ✅ test_read_from_sheet_success
# ✅ test_read_from_sheet_empty_range
# ✅ test_clear_sheet_range_success
# ✅ test_append_to_last_sheet_success
# ✅ test_append_to_sheet_by_title_success
# ✅ test_list_recent_spreadsheets_with_data
# ✅ test_find_spreadsheet_by_title_success
# ... (36 total tests covering all Google Sheets functions)

# Test Google Docs operations (mocked)
pytest tests/test_google_docs_tool.py -v

# Expected output:
# ✅ test_create_google_doc_success
# ✅ test_create_google_doc_with_sharing
# ✅ test_create_google_doc_apis_unavailable
# ✅ test_rewrite_last_doc_success
# ✅ test_rewrite_last_doc_no_recent_doc
# ✅ test_rewrite_document_success
# ✅ test_read_google_doc_success
# ✅ test_list_recent_documents_empty
# ✅ test_list_recent_documents_with_data
# ... (11 total tests covering all Google Docs functions)

# Test Google Slides operations (mocked)
pytest tests/test_google_slides_tool.py -v

# Expected output:
# ✅ test_create_google_slides_success
# ✅ test_create_google_slides_with_sharing
# ✅ test_add_slide_success
# ✅ test_add_slide_blank_layout
# ✅ test_create_slide_with_content_success
# ✅ test_add_content_to_slide_placeholders_success
# ✅ test_add_text_to_slide_success
# ✅ test_add_slide_to_last_presentation_success
# ✅ test_get_slide_info_success
# ✅ test_list_recent_presentations_with_data
# ✅ test_find_presentation_by_title_success
# ✅ test_complex_workflow_success
# ✅ test_context_management
# ... (33 total tests covering all Google Slides functions)

# Run all Google Workspace tests together
pytest tests/test_google_sheets_tool.py tests/test_google_docs_tool.py tests/test_google_slides_tool.py -v

# Expected: 80 total tests (36 + 11 + 33) covering complete Google Workspace integration
```

### Running RAG Knowledge Base Tests
```bash
# Test RAG infrastructure and vector operations (mocked)
pytest tests/test_rag_tool.py -v

# Expected output:
# ✅ test_setup_knowledge_base_success
# ✅ test_setup_knowledge_base_missing_dependencies  
# ✅ test_get_kb_health_success
# ✅ test_get_kb_health_component_error
# ✅ test_add_url_to_kb_success
# ✅ test_add_url_to_kb_crawl_failure
# ✅ test_add_text_to_kb_success
# ✅ test_add_text_to_kb_short_text
# ✅ test_search_kb_success
# ✅ test_search_kb_no_results
# ✅ test_search_kb_invalid_limit
# ✅ test_list_kb_sources_success
# ✅ test_list_kb_sources_empty_collection
# ✅ test_get_kb_stats_success
# ✅ test_get_kb_stats_no_collections
# ✅ test_tool_registration_available
# ✅ test_complex_workflow_success
# ✅ test_edge_cases_and_validation
# ... (35 total tests covering all RAG functions)

# Test categories:
# Infrastructure (7 tests): Setup, health monitoring, dependency checking
# Content Ingestion (9 tests): URL scraping, text processing, embedding generation  
# Search & Retrieval (19 tests): Semantic search, source listing, statistics, metadata handling
```

### Running Launcher Scripts Tests
```bash
# Test server launcher scripts (mocked)
pytest tests/test_launcher_scripts.py -v

# Expected output:
# ✅ test_imports_successfully
# ✅ test_detect_claude_desktop_with_env_vars
# ✅ test_detect_claude_desktop_no_tty
# ✅ test_detect_claude_desktop_force_http
# ✅ test_detect_claude_desktop_with_args
# ✅ test_detect_claude_desktop_with_tty
# ✅ test_show_help_output
# ✅ test_main_help_argument
# ✅ test_main_help_short_argument
# ✅ test_main_http_argument
# ✅ test_main_stdio_argument
# ✅ test_main_auto_detect_claude
# ✅ test_main_auto_detect_http
# ✅ test_main_force_stdio_env
# ✅ test_server_configuration
# ✅ test_server_configuration_defaults
# ✅ test_log_environment_status
# ✅ test_main_successful_startup
# ✅ test_main_keyboard_interrupt
# ✅ test_main_exception_handling
# ✅ test_main_http_transport_success
# ✅ test_main_http_fallback_to_sse
# ✅ test_main_fallback_to_default
# ✅ test_main_all_transports_fail
# ✅ test_claude_tool_registration
# ✅ test_http_tool_registration
# ✅ test_tool_import_errors_handled
# ✅ test_dotenv_loading_optional
# ✅ test_warning_suppression
# ✅ test_missing_fastmcp_handling
# ✅ test_invalid_port_handling
# ✅ test_logging_configuration
# ✅ test_run_py_docstring
# ✅ test_run_claude_docstring
# ✅ test_run_http_docstring
# ✅ test_function_docstrings
# ... (41 total tests covering all launcher functionality)

# Test categories organized by launcher script:
# Main Launcher (run.py) - 14 tests: Auto-detection, argument parsing, environment handling
# Claude Launcher (run_claude.py) - 7 tests: Stdio server configuration, startup, error handling  
# HTTP Launcher (run_http.py) - 8 tests: HTTP server setup, transport fallback mechanisms
# Tool Registration - 3 tests: Tool loading verification, import error handling
# Environment Detection - 2 tests: Optional dependency loading, warning suppression
# Error Handling - 3 tests: Missing dependencies, invalid configuration, logging setup
# Documentation - 4 tests: Docstring completeness verification

# Key testing features:
# - Environment variable isolation with proper cleanup
# - Module caching management with importlib.reload()
# - FastMCP server mocking with transport configuration
# - Comprehensive CLI argument testing (--help, --http, --stdio)
# - Claude Desktop auto-detection logic verification
# - HTTP transport fallback testing (HTTP → SSE → default)
# - Tool registration and import error scenarios
# - Startup success/failure handling with proper logging
```

## 🔍 Coverage Reports

### Generating Coverage
```bash
# HTML coverage report
pytest tests/ --cov=. --cov-report=html

# Terminal coverage report
pytest tests/ --cov=. --cov-report=term

# Coverage with specific test file
pytest tests/test_calculator_tool.py --cov=. --cov-report=term
```

### Coverage Targets
- **Overall Coverage**: >85%
- **Critical Tools**: >95% (calculator, file_system, file_writing)
- **Server Infrastructure**: >95% (launcher scripts, configuration)
- **External API Tools**: >80% (mocked paths)
- **Error Handling**: >90%

## 🐛 Debugging Tests

### Verbose Output
```bash
# Detailed test output
pytest tests/ -v -s

# Show available test markers
pytest --markers
```

### Running Single Tests
```bash
# Run specific test class
pytest tests/test_calculator_tool.py::TestCalculatorTool

# Run specific test method
pytest tests/test_calculator_tool.py::TestCalculatorTool::test_addition

# Debug mode with pdb
pytest tests/test_calculator_tool.py --pdb
```

### Common Issues

**Import Errors**
```bash
# Ensure project root in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

**Async Test Issues**
```bash
# Use asyncio mode
pytest tests/ --asyncio-mode=auto
```

**Fixture Issues**
```bash
# Debug fixtures
pytest tests/ --fixtures-per-test
```

## 📊 Test Metrics

### Performance Benchmarks
- **Unit Tests**: <50 seconds total
- **Integration Tests**: <60 seconds total
- **Full Suite**: <3 minutes total
- **Individual Tool**: <5 seconds

### Quality Metrics
- **Test Coverage**: 85%+ target
- **Pass Rate**: 100% for CI/CD
- **Flakiness**: <1% retry rate
- **Maintenance**: Weekly review cycle

## 🔧 Configuration

### pytest.ini Settings
- Async test support
- Marker definitions
- Warning filters
- Output formatting

### conftest.py Fixtures
- Mock environment variables
- Temporary file systems
- HTTP client mocking
- Server instances
- Response validation helpers

### Environment Variables
```bash
# Test environment setup
export MCP_TEST_MODE=true
export MCP_MOCK_EXTERNAL_APIS=true
export MCP_TEST_TEMP_DIR=/tmp/mcp_tests
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=. --cov-report=term --junitxml=tests/results/junit.xml
      - uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/results/
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run tests before commit
pre-commit run --all-files
```

## 📈 Continuous Improvement

### Test Development Workflow
1. **Red**: Write failing test for new feature
2. **Green**: Implement minimum code to pass
3. **Refactor**: Improve code while keeping tests green
4. **Review**: Peer review tests and implementation

### Test Maintenance
- Monthly dependency updates
- Quarterly test suite review
- Annual testing strategy evaluation
- Continuous coverage monitoring

### Future Enhancements
- [ ] Property-based testing with Hypothesis
- [ ] Load testing for high-volume scenarios
- [ ] Security testing with bandit integration
- [ ] Documentation testing with doctest
- [ ] Mutation testing for test quality

---

## 📞 Support

For test-related issues:
1. Check this README for common solutions
2. Review test output and error messages
3. Use `--verbose` flag for detailed information
4. Check GitHub issues for known problems
5. Create new issue with test reproduction steps

**Happy Testing! 🧪✨** 