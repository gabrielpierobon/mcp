# tests/test_google_sheets_tool.py
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from tools.google_sheets_tool import (
    create_google_sheet,
    write_to_sheet,
    read_from_sheet,
    clear_sheet_range,
    append_to_last_sheet,
    append_to_sheet_by_title,
    list_recent_spreadsheets,
    find_spreadsheet_by_title
)

@pytest.mark.unit
@pytest.mark.external_api
class TestGoogleSheetsTools:
    """Test suite for Google Sheets tools."""
    
    @pytest.fixture
    def mock_google_apis_available(self):
        """Mock Google APIs as available for testing."""
        with patch('tools.google_sheets_tool.GOOGLE_APIS_AVAILABLE', True):
            yield
    
    @pytest.fixture
    def mock_google_apis_unavailable(self):
        """Mock Google APIs as unavailable for testing."""
        with patch('tools.google_sheets_tool.GOOGLE_APIS_AVAILABLE', False):
            yield
    
    @pytest.fixture
    def mock_google_services(self):
        """Mock Google API services."""
        # Mock spreadsheet response
        mock_spreadsheet = {
            'spreadsheetId': 'test_sheet_id_123',
            'properties': {'title': 'Test Spreadsheet'},
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/test_sheet_id_123/edit',
            'sheets': [
                {'properties': {'title': 'Sheet1', 'sheetId': 0}},
                {'properties': {'title': 'Sheet2', 'sheetId': 1}}
            ]
        }
        
        # Mock sheets service
        mock_sheets_service = Mock()
        mock_spreadsheets = Mock()
        mock_values = Mock()
        
        # Configure sheets service methods
        mock_spreadsheets.create.return_value.execute.return_value = mock_spreadsheet
        mock_spreadsheets.get.return_value.execute.return_value = mock_spreadsheet
        mock_values.update.return_value.execute.return_value = {
            'updatedCells': 4,
            'updatedColumns': 2,
            'updatedRows': 2
        }
        mock_values.append.return_value.execute.return_value = {
            'updates': {
                'updatedCells': 4,
                'updatedColumns': 2,
                'updatedRows': 2
            }
        }
        mock_values.get.return_value.execute.return_value = {
            'values': [['Name', 'Age'], ['John', '30'], ['Jane', '25']]
        }
        mock_values.clear.return_value.execute.return_value = {
            'clearedRange': 'Sheet1!A1:B3'
        }
        
        mock_spreadsheets.values.return_value = mock_values
        mock_sheets_service.spreadsheets.return_value = mock_spreadsheets
        
        # Mock drive service
        mock_drive_service = Mock()
        mock_permissions = Mock()
        mock_permissions.create.return_value.execute.return_value = {'id': 'permission_id'}
        mock_drive_service.permissions.return_value = mock_permissions
        
        return {
            'sheets_service': mock_sheets_service,
            'drive_service': mock_drive_service,
            'spreadsheet': mock_spreadsheet
        }
    
    @pytest.fixture
    def setup_mocks(self, mock_google_apis_available, mock_google_services):
        """Setup comprehensive mocks for Google Sheets."""
        import tools.google_sheets_tool
        
        def mock_get_service(service_name, version):
            if service_name == 'sheets':
                return mock_google_services['sheets_service']
            elif service_name == 'drive':
                return mock_google_services['drive_service']
            return None
        
        # Mock the get_service function
        setattr(tools.google_sheets_tool, 'get_service', mock_get_service)
        
        # Initialize context properly
        tools.google_sheets_tool._recent_spreadsheets_context.update({
            "last_spreadsheet": None,
            "recent_spreadsheets": []
        })
        
        yield mock_google_services
        
        # Clean up context
        tools.google_sheets_tool._recent_spreadsheets_context.update({
            "last_spreadsheet": None,
            "recent_spreadsheets": []
        })

@pytest.mark.unit
@pytest.mark.external_api
class TestCreateGoogleSheet(TestGoogleSheetsTools):
    """Test create_google_sheet function."""
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_success(self, setup_mocks):
        """Test successful Google Sheet creation."""
        result = await create_google_sheet("Test Spreadsheet")
        
        assert result["status"] == "success"
        assert result["spreadsheet_id"] == "test_sheet_id_123"
        assert result["title"] == "Test Spreadsheet"
        assert result["spreadsheet_url"] == "https://docs.google.com/spreadsheets/d/test_sheet_id_123/edit"
        assert "sheets" in result
        assert len(result["sheets"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_with_custom_sheets(self, setup_mocks):
        """Test creating Google Sheet with custom sheet names."""
        custom_sheets = ["Dashboard", "Data", "Charts"]
        result = await create_google_sheet("Custom Sheet", sheet_names=custom_sheets)
        
        assert result["status"] == "success"
        assert result["title"] == "Custom Sheet"
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_with_sharing(self, setup_mocks):
        """Test creating Google Sheet with sharing."""
        emails = ["user1@example.com", "user2@example.com"]
        result = await create_google_sheet("Shared Sheet", share_with=emails)
        
        assert result["status"] == "success"
        assert "shared_with" in result
        assert result["shared_with"] == emails
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_apis_unavailable(self, mock_google_apis_unavailable):
        """Test sheet creation when Google APIs are not available."""
        result = await create_google_sheet("Test Sheet")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_service_failure(self, setup_mocks):
        """Test sheet creation with service failure."""
        # Make get_service return None
        import tools.google_sheets_tool
        setattr(tools.google_sheets_tool, 'get_service', lambda x, y: None)
        
        result = await create_google_sheet("Test Sheet")
        
        assert result["status"] == "error"
        assert "Failed to authenticate" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_google_sheet_api_exception(self, setup_mocks):
        """Test sheet creation with API exception."""
        # Make the create call raise an exception
        setup_mocks['sheets_service'].spreadsheets.return_value.create.side_effect = Exception("API Error")
        
        result = await create_google_sheet("Test Sheet")
        
        assert result["status"] == "error"
        assert "Tool execution failed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestWriteToSheet(TestGoogleSheetsTools):
    """Test write_to_sheet function."""
    
    @pytest.mark.asyncio
    async def test_write_to_sheet_success(self, setup_mocks):
        """Test successful data writing to sheet."""
        values = [["Name", "Age"], ["John", "30"], ["Jane", "25"]]
        result = await write_to_sheet("test_sheet_id", "Sheet1!A1:B3", values)
        
        assert result["status"] == "success"
        assert result["spreadsheet_id"] == "test_sheet_id"
        assert result["updated_cells"] == 4
        assert result["updated_rows"] == 2
        assert result["updated_columns"] == 2
    
    @pytest.mark.asyncio
    async def test_write_to_sheet_raw_input(self, setup_mocks):
        """Test writing to sheet with RAW input option."""
        values = [["=SUM(A1:A10)", "Raw Text"]]
        result = await write_to_sheet("test_sheet_id", "A1:B1", values, "RAW")
        
        assert result["status"] == "success"
        # The RAW option is passed to the API but not returned in the response
    
    @pytest.mark.asyncio
    async def test_write_to_sheet_apis_unavailable(self, mock_google_apis_unavailable):
        """Test writing when Google APIs are not available."""
        values = [["test"]]
        result = await write_to_sheet("test_id", "A1", values)
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_to_sheet_service_failure(self, setup_mocks):
        """Test writing with service failure."""
        import tools.google_sheets_tool
        setattr(tools.google_sheets_tool, 'get_service', lambda x, y: None)
        
        values = [["test"]]
        result = await write_to_sheet("test_id", "A1", values)
        
        assert result["status"] == "error"
        assert "Failed to authenticate" in result["error"]
    
    @pytest.mark.asyncio
    async def test_write_to_sheet_api_exception(self, setup_mocks):
        """Test writing with API exception."""
        setup_mocks['sheets_service'].spreadsheets.return_value.values.return_value.update.side_effect = Exception("Write error")
        
        values = [["test"]]
        result = await write_to_sheet("test_id", "A1", values)
        
        assert result["status"] == "error"
        assert "Tool execution failed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestReadFromSheet(TestGoogleSheetsTools):
    """Test read_from_sheet function."""
    
    @pytest.mark.asyncio
    async def test_read_from_sheet_success(self, setup_mocks):
        """Test successful data reading from sheet."""
        result = await read_from_sheet("test_sheet_id", "Sheet1!A1:B3")
        
        assert result["status"] == "success"
        assert result["spreadsheet_id"] == "test_sheet_id"
        assert result["range"] == "Sheet1!A1:B3"
        assert "values" in result
        assert len(result["values"]) == 3
        assert result["values"][0] == ["Name", "Age"]
    
    @pytest.mark.asyncio
    async def test_read_from_sheet_empty_range(self, setup_mocks):
        """Test reading from empty range."""
        # Mock empty response
        setup_mocks['sheets_service'].spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {}
        
        result = await read_from_sheet("test_sheet_id", "Sheet1!Z1:Z10")
        
        assert result["status"] == "success"
        assert result["values"] == []
    
    @pytest.mark.asyncio
    async def test_read_from_sheet_apis_unavailable(self, mock_google_apis_unavailable):
        """Test reading when Google APIs are not available."""
        result = await read_from_sheet("test_id", "A1")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_read_from_sheet_api_exception(self, setup_mocks):
        """Test reading with API exception."""
        setup_mocks['sheets_service'].spreadsheets.return_value.values.return_value.get.side_effect = Exception("Read error")
        
        result = await read_from_sheet("test_id", "A1")
        
        assert result["status"] == "error"
        assert "Tool execution failed" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestClearSheetRange(TestGoogleSheetsTools):
    """Test clear_sheet_range function."""
    
    @pytest.mark.asyncio
    async def test_clear_sheet_range_success(self, setup_mocks):
        """Test successful range clearing."""
        result = await clear_sheet_range("test_sheet_id", "Sheet1!A1:B3")
        
        assert result["status"] == "success"
        assert result["spreadsheet_id"] == "test_sheet_id"
        assert result["cleared_range"] == "Sheet1!A1:B3"
    
    @pytest.mark.asyncio
    async def test_clear_sheet_range_apis_unavailable(self, mock_google_apis_unavailable):
        """Test clearing when Google APIs are not available."""
        result = await clear_sheet_range("test_id", "A1")
        
        assert result["status"] == "error"
        assert "Google API client libraries are not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_clear_sheet_range_api_exception(self, setup_mocks):
        """Test clearing with API exception."""
        setup_mocks['sheets_service'].spreadsheets.return_value.values.return_value.clear.side_effect = Exception("Clear error")
        
        result = await clear_sheet_range("test_id", "A1")
        
        assert result["status"] == "error"
        assert "Tool execution failed: Clear error" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAppendToLastSheet(TestGoogleSheetsTools):
    """Test append_to_last_sheet function."""
    
    @pytest.mark.asyncio
    async def test_append_to_last_sheet_success(self, setup_mocks):
        """Test successful appending to last sheet."""
        # First create a sheet to have a "last sheet"
        await create_google_sheet("Test Sheet")
        
        values = [["New Row 1", "Data 1"], ["New Row 2", "Data 2"]]
        result = await append_to_last_sheet(values)
        
        assert result["status"] == "success"
        assert "spreadsheet_id" in result
        assert "appended_to" in result
    
    @pytest.mark.asyncio
    async def test_append_to_last_sheet_with_start_row(self, setup_mocks):
        """Test appending to last sheet with specific start row."""
        await create_google_sheet("Test Sheet")
        
        values = [["Row at 5", "Data"]]
        result = await append_to_last_sheet(values, start_row=5)
        
        assert result["status"] == "success"
        assert "appended_to" in result
        assert result["appended_to"]["start_row"] == 5
    
    @pytest.mark.asyncio
    async def test_append_to_last_sheet_custom_sheet_name(self, setup_mocks):
        """Test appending to specific sheet in last spreadsheet."""
        await create_google_sheet("Test Sheet")
        
        values = [["Custom sheet data"]]
        result = await append_to_last_sheet(values, sheet_name="Sheet2")
        
        assert result["status"] == "success"
        assert "appended_to" in result
        assert result["appended_to"]["sheet_name"] == "Sheet2"
    
    @pytest.mark.asyncio
    async def test_append_to_last_sheet_no_recent_sheet(self, setup_mocks):
        """Test appending when no recent sheet exists."""
        values = [["test"]]
        result = await append_to_last_sheet(values)
        
        assert result["status"] == "error"
        assert "No recent spreadsheet found" in result["error"]

@pytest.mark.unit
@pytest.mark.external_api
class TestAppendToSheetByTitle(TestGoogleSheetsTools):
    """Test append_to_sheet_by_title function."""
    
    @pytest.mark.asyncio
    async def test_append_to_sheet_by_title_success(self, setup_mocks):
        """Test successful appending by title search."""
        # Create a sheet first
        await create_google_sheet("My Test Spreadsheet")
        
        values = [["Searched data", "Found it"]]
        result = await append_to_sheet_by_title("Test", values)
        
        assert result["status"] == "success"
        assert "spreadsheet_id" in result
        assert "appended_to" in result
    
    @pytest.mark.asyncio
    async def test_append_to_sheet_by_title_not_found(self, setup_mocks):
        """Test appending when title search finds no matches."""
        await create_google_sheet("My Spreadsheet")
        
        values = [["test"]]
        result = await append_to_sheet_by_title("NonExistent", values)
        
        assert result["status"] == "error"
        assert "No spreadsheet found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_append_to_sheet_by_title_multiple_matches(self, setup_mocks):
        """Test appending when multiple sheets match the search."""
        # Create multiple sheets with similar names
        await create_google_sheet("Test Sheet 1")
        await create_google_sheet("Test Sheet 2")
        
        values = [["test"]]
        result = await append_to_sheet_by_title("Test", values)
        
        # Should use the most recent (first) match
        assert result["status"] == "success"

@pytest.mark.unit
@pytest.mark.external_api
class TestContextMemoryFunctions(TestGoogleSheetsTools):
    """Test context memory and utility functions."""
    
    @pytest.mark.asyncio
    async def test_list_recent_spreadsheets_empty(self, setup_mocks):
        """Test listing recent spreadsheets when none exist."""
        result = await list_recent_spreadsheets()
        
        assert result["status"] == "success"
        assert result["recent_spreadsheets"] == []
        assert result["last_spreadsheet"] is None
        assert result["count"] == 0
    
    @pytest.mark.asyncio
    async def test_list_recent_spreadsheets_with_data(self, setup_mocks):
        """Test listing recent spreadsheets with existing data."""
        # Create some sheets
        await create_google_sheet("Sheet 1")
        await create_google_sheet("Sheet 2")
        await create_google_sheet("Sheet 3")
        
        result = await list_recent_spreadsheets()
        
        assert result["status"] == "success"
        assert result["count"] == 3
        assert len(result["recent_spreadsheets"]) == 3
        assert result["last_spreadsheet"]["title"] == "Sheet 3"  # Most recent
        assert result["recent_spreadsheets"][0]["title"] == "Sheet 3"  # First in list
    
    @pytest.mark.asyncio
    async def test_find_spreadsheet_by_title_success(self, setup_mocks):
        """Test finding spreadsheet by title."""
        await create_google_sheet("Project Budget")
        await create_google_sheet("Team Schedule")
        await create_google_sheet("Budget Analysis")
        
        result = await find_spreadsheet_by_title("Budget")
        
        assert result["status"] == "success"
        assert result["search_term"] == "Budget"
        assert result["count"] == 2
        assert len(result["matching_spreadsheets"]) == 2
        
        # Check that both budget-related sheets are found
        titles = [sheet["title"] for sheet in result["matching_spreadsheets"]]
        assert "Project Budget" in titles
        assert "Budget Analysis" in titles
    
    @pytest.mark.asyncio
    async def test_find_spreadsheet_by_title_case_insensitive(self, setup_mocks):
        """Test case-insensitive title search."""
        await create_google_sheet("UPPERCASE SHEET")
        await create_google_sheet("lowercase sheet")
        await create_google_sheet("MiXeD cAsE sheet")
        
        result = await find_spreadsheet_by_title("SHEET")
        
        assert result["status"] == "success"
        assert result["count"] == 3  # Should find all three
    
    @pytest.mark.asyncio
    async def test_find_spreadsheet_by_title_no_matches(self, setup_mocks):
        """Test finding spreadsheet when no matches exist."""
        await create_google_sheet("Test Sheet")
        
        result = await find_spreadsheet_by_title("NonExistent")
        
        assert result["status"] == "success"
        assert result["count"] == 0
        assert result["matching_spreadsheets"] == []
        assert len(result["all_available_titles"]) == 1

@pytest.mark.integration
class TestGoogleSheetsToolRegistration:
    """Test tool registration."""
    
    def test_tool_registration_available(self):
        """Test tool registration when Google APIs are available."""
        mock_mcp = Mock()
        mock_tool = Mock()
        mock_mcp.tool.return_value = mock_tool
        
        with patch('tools.google_sheets_tool.GOOGLE_APIS_AVAILABLE', True):
            from tools.google_sheets_tool import register
            register(mock_mcp)
        
        # Should register all 8 tools
        assert mock_mcp.tool.call_count == 8
    
    def test_tool_registration_unavailable(self):
        """Test tool registration when Google APIs are not available."""
        mock_mcp = Mock()
        
        with patch('tools.google_sheets_tool.GOOGLE_APIS_AVAILABLE', False):
            from tools.google_sheets_tool import register
            register(mock_mcp)
        
        # Should not register any tools
        mock_mcp.tool.assert_not_called()

@pytest.mark.unit
class TestErrorHandling(TestGoogleSheetsTools):
    """Test comprehensive error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_complex_workflow_success(self, setup_mocks):
        """Test a complex workflow with multiple operations."""
        # Create spreadsheet
        create_result = await create_google_sheet("Workflow Test", ["Data", "Analysis"])
        assert create_result["status"] == "success"
        
        spreadsheet_id = create_result["spreadsheet_id"]
        
        # Write initial data
        initial_data = [["Name", "Score"], ["Alice", "95"], ["Bob", "87"]]
        write_result = await write_to_sheet(spreadsheet_id, "Data!A1:B3", initial_data)
        assert write_result["status"] == "success"
        
        # Read data back
        read_result = await read_from_sheet(spreadsheet_id, "Data!A1:B3")
        assert read_result["status"] == "success"
        assert len(read_result["values"]) == 3
        
        # Append more data using context functions
        append_data = [["Charlie", "92"], ["Diana", "98"]]
        append_result = await append_to_last_sheet(append_data)
        assert append_result["status"] == "success"
        
        # Find and append by title
        title_append_result = await append_to_sheet_by_title("Workflow", [["Eve", "90"]])
        assert title_append_result["status"] == "success"
        
        # List recent spreadsheets
        list_result = await list_recent_spreadsheets()
        assert list_result["status"] == "success"
        assert list_result["count"] == 1
        
        # Clear a range
        clear_result = await clear_sheet_range(spreadsheet_id, "Analysis!A1:Z100")
        assert clear_result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_context_management(self, setup_mocks):
        """Test that context management works correctly."""
        # Create multiple sheets
        sheets = []
        for i in range(3):
            result = await create_google_sheet(f"Test Sheet {i+1}")
            assert result["status"] == "success"
            sheets.append(result)
        
        # Test context storage
        context_result = await list_recent_spreadsheets()
        assert context_result["count"] == 3
        assert context_result["last_spreadsheet"]["title"] == "Test Sheet 3"
        
        # Test search functionality
        search_result = await find_spreadsheet_by_title("Sheet 2")
        assert search_result["count"] == 1
        assert search_result["matching_spreadsheets"][0]["title"] == "Test Sheet 2"
        
        # Test append to specific sheet by title
        append_result = await append_to_sheet_by_title("Sheet 1", [["test", "data"]])
        assert append_result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_edge_cases_and_validation(self, setup_mocks):
        """Test edge cases and input validation."""
        # Empty title
        result = await create_google_sheet("")
        assert result["status"] == "success"  # Should still work with empty title
        
        # Empty values array
        empty_write_result = await write_to_sheet("test_id", "A1", [])
        assert empty_write_result["status"] == "success"
        
        # Very large range
        large_range_result = await read_from_sheet("test_id", "A1:ZZ10000")
        assert large_range_result["status"] == "success"
        
        # Special characters in sheet names
        special_result = await create_google_sheet("Test 'Sheet' with \"Quotes\" & Symbols!")
        assert special_result["status"] == "success"

@pytest.mark.unit
class TestToolRegistration:
    """Test tool registration."""
    
    def test_basic_registration(self):
        """Basic registration test."""
        mock_mcp = Mock()
        mock_tool = Mock()
        mock_mcp.tool.return_value = mock_tool
        
        with patch('tools.google_sheets_tool.GOOGLE_APIS_AVAILABLE', True):
            from tools.google_sheets_tool import register
            register(mock_mcp)
        
        # Should register tools when available
        assert mock_mcp.tool.call_count > 0 