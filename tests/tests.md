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
- ⏳ Airtable Tool (database operations, mocked)
- ⏳ Web Crawling Tool (Crawl4AI, mocked)
- ⏳ Browser Automation (Playwright, mocked)
- ⏳ Google Workspace Tools (Sheets, Docs, Slides, mocked)
- ⏳ RAG Knowledge Base (vector operations, mocked)

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt
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
├── 📄 requirements-test.txt    # Test dependencies

├── 📄 README.md               # This file
│
├── 🔧 Unit Tests
│   ├── test_calculator_tool.py      # ✅ Calculator operations
│   ├── test_brave_search.py         # ✅ Web search (mocked)
│   ├── test_weather_tool.py         # ✅ Weather API (mocked)
│   ├── test_file_system_tool.py     # ✅ File operations
│   ├── test_file_writing_tool.py    # ✅ File writing & security
│   ├── test_screen_capture_tool.py  # ✅ Screen capture (mocked)
│   ├── test_airtable_tool.py        # ⏳ Database operations
│   ├── test_crawl4ai_tool.py        # ⏳ Web crawling
│   ├── test_playwright_tool.py      # ⏳ Browser automation
│   ├── test_google_sheets_tool.py   # ⏳ Google Sheets
│   ├── test_google_docs_tool.py     # ⏳ Google Docs
│   ├── test_google_slides_tool.py   # ⏳ Google Slides
│   └── test_rag_tool.py             # ⏳ Knowledge base
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
- **Unit Tests**: <30 seconds total
- **Integration Tests**: <60 seconds total
- **Full Suite**: <2 minutes total
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
      - run: python tests/run_tests.py --install-deps
      - run: python tests/run_tests.py --coverage --junit
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