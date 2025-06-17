import pytest
import asyncio
from unittest.mock import patch, AsyncMock, Mock
from typing import Dict, Any
import httpx
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the tool functions
from tools.airtable_tool import (
    create_airtable_base,
    create_airtable_table,
    list_airtable_bases,
    get_base_schema,
    create_base_with_template,
    list_records,
    search_records,
    get_record_by_id,
    count_records,
    get_base_by_name,
    list_records_by_base_name,
    validate_base_and_table,
    search_records_by_base_name,
    get_airtable_headers
)

# Test class for Airtable base operations
@pytest.mark.unit
@pytest.mark.external_api
class TestAirtableBaseOperations:
    """Test Airtable base creation and management operations."""
    
    @pytest.mark.asyncio
    async def test_create_airtable_base_success(self, mock_env_vars):
        """Test successful base creation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "appTest123"}'
        mock_response.json.return_value = {
            "id": "appTest123",
            "name": "Test Base",
            "permissionLevel": "owner",
            "tables": [
                {
                    "id": "tblTest456",
                    "name": "Table 1",
                    "primaryFieldId": "fldTest789"
                }
            ]
        }
        
        # Mock the httpx client directly
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client.get.return_value = mock_response  # for workspace lookup
            
            # Test the function
            result = await create_airtable_base("Test Base")
            
            # Assertions
            assert result["status"] == "success"
            assert result["base_id"] == "appTest123"
            assert result["name"] == "Test Base"
            assert result["permission_level"] == "owner"
            assert len(result["tables"]) == 1
    
    @pytest.mark.asyncio
    async def test_create_airtable_base_no_token(self):
        """Test base creation without API token."""
        with patch('tools.airtable_tool.AIRTABLE_PERSONAL_ACCESS_TOKEN', None):
            result = await create_airtable_base("Test Base")
            
            assert result["status"] == "error"
            assert "AIRTABLE_PERSONAL_ACCESS_TOKEN" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_airtable_base_with_custom_tables(self, mock_env_vars):
        """Test base creation with custom table configuration."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "appTest123"}'
        mock_response.json.return_value = {
            "id": "appTest123",
            "name": "Custom Base",
            "permissionLevel": "owner",
            "tables": []
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client.get.return_value = mock_response
            
            # Test with custom tables
            custom_tables = [
                {
                    "name": "Projects",
                    "description": "Project tracking table",
                    "fields": [
                        {"name": "Project Name", "type": "singleLineText"},
                        {"name": "Status", "type": "singleSelect", "options": {"choices": [{"name": "Active"}, {"name": "Complete"}]}}
                    ]
                }
            ]
            
            result = await create_airtable_base("Custom Base", tables=custom_tables)
            
            assert result["status"] == "success"
            assert result["base_id"] == "appTest123"
    
    @pytest.mark.asyncio
    async def test_create_airtable_base_api_error(self, mock_env_vars):
        """Test base creation with API error response."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"error": {"type": "INVALID_REQUEST_UNKNOWN"}}'
        mock_response.json.return_value = {
            "error": {
                "type": "INVALID_REQUEST_UNKNOWN",
                "message": "Invalid request"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client.get.return_value = mock_response
            
            result = await create_airtable_base("Test Base")
            
            assert result["status"] == "error"
            assert "Failed to create base" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_airtable_base_network_error(self, mock_env_vars):
        """Test base creation with network error."""
        # Mock network error
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.ConnectError("Connection failed")
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            
            result = await create_airtable_base("Test Base")
            
            assert result["status"] == "error"
            assert "Tool execution failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_airtable_table_success(self, mock_env_vars):
        """Test successful table creation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "tblNewTable123"}'
        mock_response.json.return_value = {
            "id": "tblNewTable123",
            "name": "New Table",
            "primaryFieldId": "fldPrimary456",
            "fields": [
                {
                    "id": "fldPrimary456",
                    "name": "Name",
                    "type": "singleLineText"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            
            result = await create_airtable_table("appTest123", "New Table")
            
            assert result["status"] == "success"
            assert result["table_id"] == "tblNewTable123"
            assert result["name"] == "New Table"
    
    @pytest.mark.asyncio
    async def test_list_airtable_bases_success(self, mock_env_vars):
        """Test successful listing of bases."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"bases": []}'
        mock_response.json.return_value = {
            "bases": [
                {
                    "id": "appBase1",
                    "name": "Base 1",
                    "permissionLevel": "owner"
                },
                {
                    "id": "appBase2", 
                    "name": "Base 2",
                    "permissionLevel": "editor"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await list_airtable_bases()
            
            assert result["status"] == "success"
            assert len(result["bases"]) == 2
            assert result["bases"][0]["id"] == "appBase1"
    
    @pytest.mark.asyncio
    async def test_get_base_schema_success(self, mock_env_vars):
        """Test successful base schema retrieval."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"tables": []}'
        mock_response.json.return_value = {
            "tables": [
                {
                    "id": "tblTable1",
                    "name": "Projects",
                    "primaryFieldId": "fldName",
                    "fields": [
                        {
                            "id": "fldName",
                            "name": "Name",
                            "type": "singleLineText"
                        },
                        {
                            "id": "fldStatus",
                            "name": "Status",
                            "type": "singleSelect"
                        }
                    ]
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await get_base_schema("appTest123")
            
            assert result["status"] == "success"
            assert len(result["tables"]) == 1
            assert result["tables"][0]["name"] == "Projects"
            assert len(result["tables"][0]["fields"]) == 2


# Test class for Airtable template operations
@pytest.mark.unit
@pytest.mark.external_api
class TestAirtableTemplates:
    """Test Airtable template-based base creation."""
    
    @pytest.mark.asyncio
    async def test_create_base_with_template_project_management(self, mock_env_vars):
        """Test creating base with project management template."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "appProject123"}'
        mock_response.json.return_value = {
            "id": "appProject123",
            "name": "My Project Tracker",
            "permissionLevel": "owner",
            "tables": []
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client.get.return_value = mock_response
            
            result = await create_base_with_template("My Project Tracker", "project_management")
            
            assert result["status"] == "success"
            assert result["base_id"] == "appProject123"
            assert result["name"] == "My Project Tracker"
    
    @pytest.mark.asyncio
    async def test_create_base_with_template_crm(self, mock_env_vars):
        """Test creating base with CRM template."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "appCRM123"}'
        mock_response.json.return_value = {
            "id": "appCRM123",
            "name": "Customer Database",
            "permissionLevel": "owner",
            "tables": []
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client.get.return_value = mock_response
            
            result = await create_base_with_template("Customer Database", "crm")
            
            assert result["status"] == "success"
            assert result["base_id"] == "appCRM123"
    
    @pytest.mark.asyncio
    async def test_create_base_with_invalid_template(self, mock_env_vars):
        """Test creating base with invalid template."""
        result = await create_base_with_template("Test Base", "invalid_template")
        
        assert result["status"] == "error"
        assert "Unknown template" in result["error"]


# Test class for Airtable record operations
@pytest.mark.unit
@pytest.mark.external_api
class TestAirtableRecordOperations:
    """Test Airtable record CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_list_records_success(self, mock_env_vars):
        """Test successful record listing."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [
                {
                    "id": "recRecord1",
                    "fields": {
                        "Name": "Project Alpha",
                        "Status": "Active"
                    },
                    "createdTime": "2024-01-01T00:00:00.000Z"
                },
                {
                    "id": "recRecord2",
                    "fields": {
                        "Name": "Project Beta",
                        "Status": "Complete"
                    },
                    "createdTime": "2024-01-02T00:00:00.000Z"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await list_records("appTest123", "Projects")
            
            assert result["status"] == "success"
            assert len(result["records"]) == 2
            assert result["records"][0]["fields"]["Name"] == "Project Alpha"
    
    @pytest.mark.asyncio
    async def test_list_records_with_filters(self, mock_env_vars):
        """Test record listing with filters and sorting."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [
                {
                    "id": "recRecord1",
                    "fields": {
                        "Name": "Active Project",
                        "Status": "Active"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await list_records(
                "appTest123", 
                "Projects",
                fields=["Name", "Status"],
                filter_formula='{Status} = "Active"',
                max_records=10,
                sort=[{"field": "Name", "direction": "asc"}]
            )
            
            assert result["status"] == "success"
            assert len(result["records"]) == 1
    
    @pytest.mark.asyncio
    async def test_search_records_exact_match(self, mock_env_vars):
        """Test searching records with exact match."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [
                {
                    "id": "recFound1",
                    "fields": {
                        "Name": "Project Alpha",
                        "Status": "Active"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await search_records(
                "appTest123",
                "Projects", 
                "Name",
                "Project Alpha",
                match_type="exact"
            )
            
            assert result["status"] == "success"
            assert len(result["records"]) == 1
            assert result["records"][0]["fields"]["Name"] == "Project Alpha"
    
    @pytest.mark.asyncio
    async def test_search_records_contains_match(self, mock_env_vars):
        """Test searching records with contains match."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [
                {
                    "id": "recFound1",
                    "fields": {
                        "Name": "Project Alpha Test",
                        "Status": "Active"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await search_records(
                "appTest123",
                "Projects",
                "Name", 
                "Alpha",
                match_type="contains"
            )
            
            assert result["status"] == "success"
            assert len(result["records"]) == 1
    
    @pytest.mark.asyncio
    async def test_get_record_by_id_success(self, mock_env_vars):
        """Test successful record retrieval by ID."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"id": "recSpecific123"}'
        mock_response.json.return_value = {
            "id": "recSpecific123",
            "fields": {
                "Name": "Specific Project",
                "Status": "In Progress",
                "Description": "A detailed project description"
            },
            "createdTime": "2024-01-01T00:00:00.000Z"
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await get_record_by_id("appTest123", "Projects", "recSpecific123")
            
            assert result["status"] == "success"
            assert result["record"]["id"] == "recSpecific123"
            assert result["record"]["fields"]["Name"] == "Specific Project"
    
    @pytest.mark.asyncio
    async def test_get_record_by_id_not_found(self, mock_env_vars):
        """Test record retrieval when record not found."""
        # Mock not found response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"error": {"type": "NOT_FOUND"}}'
        mock_response.json.return_value = {
            "error": {
                "type": "NOT_FOUND",
                "message": "Record not found"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await get_record_by_id("appTest123", "Projects", "recNonExistent")
            
            assert result["status"] == "error"
            assert "404" in result["error"]
    
    @pytest.mark.asyncio
    async def test_count_records_success(self, mock_env_vars):
        """Test successful record counting."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [{"id": f"rec{i}"} for i in range(25)]  # 25 records
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await count_records("appTest123", "Projects")
            
            assert result["status"] == "success"
            assert result["count"] == 25
    
    @pytest.mark.asyncio
    async def test_count_records_with_filter(self, mock_env_vars):
        """Test record counting with filter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"records": []}'
        mock_response.json.return_value = {
            "records": [{"id": f"rec{i}"} for i in range(10)]  # 10 filtered records
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await count_records(
                "appTest123", 
                "Projects",
                filter_formula='{Status} = "Active"'
            )
            
            assert result["status"] == "success"
            assert result["count"] == 10


# Test class for Airtable convenience functions
@pytest.mark.unit
@pytest.mark.external_api
class TestAirtableConvenienceFunctions:
    """Test Airtable convenience functions that work with base names."""
    
    @pytest.mark.asyncio
    async def test_get_base_by_name_success(self, mock_env_vars):
        """Test successful base retrieval by name."""
        # Mock successful response for listing bases
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"bases": []}'
        mock_response.json.return_value = {
            "bases": [
                {
                    "id": "appBase1",
                    "name": "Project Tracker",
                    "permissionLevel": "owner"
                },
                {
                    "id": "appBase2",
                    "name": "Customer Database", 
                    "permissionLevel": "editor"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await get_base_by_name("Project Tracker")
            
            assert result["status"] == "success"
            assert result["base_id"] == "appBase1"
            assert result["permission_level"] == "owner"
    
    @pytest.mark.asyncio
    async def test_get_base_by_name_not_found(self, mock_env_vars):
        """Test base retrieval when base name not found."""
        # Mock successful response with no matching base
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"bases": []}'
        mock_response.json.return_value = {
            "bases": [
                {
                    "id": "appBase1",
                    "name": "Different Base",
                    "permissionLevel": "owner"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await get_base_by_name("Nonexistent Base")
            
            assert result["status"] == "error"
            assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_records_by_base_name_success(self, mock_env_vars):
        """Test listing records using base name instead of ID."""
        # Mock responses for both getting base by name and listing records
        base_response = Mock()
        base_response.status_code = 200
        base_response.headers = {"content-type": "application/json"}
        base_response.text = '{"bases": []}'
        base_response.json.return_value = {
            "bases": [
                {
                    "id": "appFoundBase",
                    "name": "Project Tracker",
                    "permissionLevel": "owner"
                }
            ]
        }
        
        records_response = Mock()
        records_response.status_code = 200
        records_response.headers = {"content-type": "application/json"}
        records_response.text = '{"records": []}'
        records_response.json.return_value = {
            "records": [
                {
                    "id": "recRecord1",
                    "fields": {
                        "Name": "Task 1",
                        "Status": "Complete"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = [base_response, records_response]
            
            result = await list_records_by_base_name("Project Tracker", "Tasks")
            
            assert result["status"] == "success"
            assert len(result["records"]) == 1
            assert result["records"][0]["fields"]["Name"] == "Task 1"
    
    @pytest.mark.asyncio
    async def test_validate_base_and_table_success(self, mock_env_vars):
        """Test successful base and table validation."""
        # Mock responses for getting base and schema
        base_response = Mock()
        base_response.status_code = 200
        base_response.headers = {"content-type": "application/json"}
        base_response.text = '{"bases": []}'
        base_response.json.return_value = {
            "bases": [
                {
                    "id": "appValidBase",
                    "name": "Project Tracker",
                    "permissionLevel": "owner"
                }
            ]
        }
        
        schema_response = Mock()
        schema_response.status_code = 200
        schema_response.headers = {"content-type": "application/json"}
        schema_response.text = '{"tables": []}'
        schema_response.json.return_value = {
            "tables": [
                {
                    "id": "tblTasks",
                    "name": "Tasks",
                    "primaryFieldId": "fldName"
                },
                {
                    "id": "tblProjects",
                    "name": "Projects", 
                    "primaryFieldId": "fldName"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = [base_response, schema_response]
            
            result = await validate_base_and_table("Project Tracker", "Tasks")
            
            assert result["status"] == "success"
            assert result["validation"] == "success"
            assert result["base_id"] == "appValidBase"
            assert result["table_id"] == "tblTasks"
    
    @pytest.mark.asyncio
    async def test_validate_base_and_table_table_not_found(self, mock_env_vars):
        """Test validation when table is not found in base."""
        # Mock responses for getting base and schema
        base_response = Mock()
        base_response.status_code = 200
        base_response.headers = {"content-type": "application/json"}
        base_response.text = '{"bases": []}'
        base_response.json.return_value = {
            "bases": [
                {
                    "id": "appValidBase",
                    "name": "Project Tracker",
                    "permissionLevel": "owner"
                }
            ]
        }
        
        schema_response = Mock()
        schema_response.status_code = 200
        schema_response.headers = {"content-type": "application/json"}
        schema_response.text = '{"tables": []}'
        schema_response.json.return_value = {
            "tables": [
                {
                    "id": "tblProjects",
                    "name": "Projects",
                    "primaryFieldId": "fldName"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = [base_response, schema_response]
            
            result = await validate_base_and_table("Project Tracker", "NonexistentTable")
            
            assert result["status"] == "error"
            assert "available_tables" in result
            assert len(result["available_tables"]) == 1
            assert result["base_id"] == "appValidBase"
    
    @pytest.mark.asyncio
    async def test_search_records_by_base_name_success(self, mock_env_vars):
        """Test searching records using base name."""
        # Mock responses for getting base by name and searching records
        base_response = Mock()
        base_response.status_code = 200
        base_response.headers = {"content-type": "application/json"}
        base_response.text = '{"bases": []}'
        base_response.json.return_value = {
            "bases": [
                {
                    "id": "appSearchBase",
                    "name": "Customer DB",
                    "permissionLevel": "owner"
                }
            ]
        }
        
        search_response = Mock()
        search_response.status_code = 200
        search_response.headers = {"content-type": "application/json"}
        search_response.text = '{"records": []}'
        search_response.json.return_value = {
            "records": [
                {
                    "id": "recCustomer1",
                    "fields": {
                        "Company": "ACME Corp",
                        "Status": "Active"
                    }
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = [base_response, search_response]
            
            result = await search_records_by_base_name(
                "Customer DB", 
                "Companies",
                "Company",
                "ACME Corp"
            )
            
            assert result["status"] == "success"
            assert len(result["records"]) == 1
            assert result["records"][0]["fields"]["Company"] == "ACME Corp"


# Test class for utility functions
@pytest.mark.unit
class TestAirtableUtilities:
    """Test Airtable utility functions."""
    
    def test_get_airtable_headers_with_token(self, mock_env_vars):
        """Test header generation with valid token."""
        with patch('tools.airtable_tool.AIRTABLE_PERSONAL_ACCESS_TOKEN', 'test_airtable_token'):
            headers = get_airtable_headers()
            
            assert headers is not None
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test_airtable_token"
            assert headers["Content-Type"] == "application/json"
    
    def test_get_airtable_headers_without_token(self):
        """Test header generation without token."""
        with patch('tools.airtable_tool.AIRTABLE_PERSONAL_ACCESS_TOKEN', None):
            headers = get_airtable_headers()
            
            assert headers is None


# Test class for error handling
@pytest.mark.unit
@pytest.mark.external_api
class TestAirtableErrorHandling:
    """Test error handling across all Airtable functions."""
    
    @pytest.mark.asyncio
    async def test_network_timeout_error(self, mock_env_vars):
        """Test handling of network timeout errors."""
        # Mock timeout error
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            
            result = await list_airtable_bases()
            
            assert result["status"] == "error"
            assert "Tool execution failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access_error(self, mock_env_vars):
        """Test handling of unauthorized access errors."""
        # Mock 401 unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"error": {"type": "AUTHENTICATION_REQUIRED"}}'
        mock_response.json.return_value = {
            "error": {
                "type": "AUTHENTICATION_REQUIRED",
                "message": "Unauthorized"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await list_airtable_bases()
            
            assert result["status"] == "error"
            assert "401" in result["error"]
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_env_vars):
        """Test handling of rate limit errors."""
        # Mock 429 rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"error": {"type": "REQUEST_TOO_MANY"}}'
        mock_response.json.return_value = {
            "error": {
                "type": "REQUEST_TOO_MANY",
                "message": "Too many requests"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            
            result = await list_records("appTest123", "Table1")
            
            assert result["status"] == "error"
            assert "429" in result["error"]


# Integration test for tool registration
@pytest.mark.integration
class TestAirtableToolRegistration:
    """Test Airtable tool registration with FastMCP server."""
    
    def test_tool_registration(self, fastmcp_server):
        """Test that all Airtable tools are properly registered."""
        from tools.airtable_tool import register
        
        # Register the tools
        register(fastmcp_server)
        
        # Check that tools were registered
        expected_tools = [
            "create_airtable_base",
            "create_airtable_table", 
            "list_airtable_bases",
            "get_base_schema",
            "create_base_with_template",
            "list_records",
            "search_records",
            "get_record_by_id",
            "count_records",
            "get_base_by_name",
            "list_records_by_base_name",
            "validate_base_and_table",
            "search_records_by_base_name"
        ]
        
        # Verify tools were registered
        assert fastmcp_server.tool.call_count == len(expected_tools)
        
        # Check that all expected tool names are in registered functions
        for tool_name in expected_tools:
            assert tool_name in fastmcp_server._registered_functions 