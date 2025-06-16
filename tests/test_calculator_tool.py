import pytest
from tools.calculator_tool import calculator, register


class TestCalculatorTool:
    """Test suite for the calculator tool."""
    
    @pytest.mark.asyncio
    async def test_addition(self, assert_success_response):
        """Test addition operation."""
        result = await calculator("add", 5, 3)
        assert_success_response(result)
        assert result["result"] == 8
        assert "5 + 3 = 8" in result["description"]
    
    @pytest.mark.asyncio 
    async def test_subtraction(self, assert_success_response):
        """Test subtraction operation."""
        result = await calculator("subtract", 10, 4)
        assert_success_response(result)
        assert result["result"] == 6
        assert "10 - 4 = 6" in result["description"]
    
    @pytest.mark.asyncio
    async def test_multiplication(self, assert_success_response):
        """Test multiplication operation."""
        result = await calculator("multiply", 6, 7)
        assert_success_response(result)
        assert result["result"] == 42
        assert "6 × 7 = 42" in result["description"]
    
    @pytest.mark.asyncio
    async def test_division(self, assert_success_response):
        """Test division operation."""
        result = await calculator("divide", 15, 3)
        assert_success_response(result)
        assert result["result"] == 5
        assert "15 ÷ 3 = 5" in result["description"]
    
    @pytest.mark.asyncio
    async def test_division_by_zero(self, assert_error_response):
        """Test division by zero error handling."""
        result = await calculator("divide", 10, 0)
        assert_error_response(result, "Division by zero")
    
    @pytest.mark.asyncio
    async def test_invalid_operation(self, assert_error_response):
        """Test invalid operation error handling."""
        result = await calculator("invalid_op", 5, 3)
        assert_error_response(result, "Unknown operation")
    
    @pytest.mark.asyncio
    async def test_operation_aliases(self, assert_success_response):
        """Test operation symbol aliases."""
        # Test + alias
        result = await calculator("+", 2, 3)
        assert_success_response(result)
        assert result["result"] == 5
        
        # Test - alias
        result = await calculator("-", 10, 5)
        assert_success_response(result)
        assert result["result"] == 5
        
        # Test * alias
        result = await calculator("*", 4, 5)
        assert_success_response(result)
        assert result["result"] == 20
        
        # Test / alias
        result = await calculator("/", 20, 4)
        assert_success_response(result)
        assert result["result"] == 5
    
    @pytest.mark.asyncio
    async def test_case_insensitive_operations(self, assert_success_response):
        """Test that operations are case insensitive."""
        result = await calculator("ADD", 5, 3)
        assert_success_response(result)
        assert result["result"] == 8
        
        result = await calculator("MULTIPLY", 6, 7)
        assert_success_response(result)
        assert result["result"] == 42
    
    @pytest.mark.asyncio
    async def test_floating_point_numbers(self, assert_success_response):
        """Test calculations with floating point numbers."""
        result = await calculator("add", 2.5, 3.7)
        assert_success_response(result)
        assert result["result"] == 6.2
        
        result = await calculator("divide", 7.5, 2.5)
        assert_success_response(result)
        assert result["result"] == 3.0
    
    @pytest.mark.asyncio
    async def test_negative_numbers(self, assert_success_response):
        """Test calculations with negative numbers."""
        result = await calculator("add", -5, 3)
        assert_success_response(result)
        assert result["result"] == -2
        
        result = await calculator("multiply", -4, -3)
        assert_success_response(result)
        assert result["result"] == 12
    
    @pytest.mark.asyncio
    async def test_large_numbers(self, assert_success_response):
        """Test calculations with large numbers."""
        result = await calculator("multiply", 1000000, 1000000)
        assert_success_response(result)
        assert result["result"] == 1000000000000
    
    @pytest.mark.asyncio
    async def test_parametrized_operations(self, sample_calculation_data, assert_success_response):
        """Test multiple operations using parametrized data."""
        for test_case in sample_calculation_data:
            result = await calculator(
                test_case["operation"], 
                test_case["num1"], 
                test_case["num2"]
            )
            assert_success_response(result)
            assert result["result"] == test_case["expected"]
    
    def test_registration(self, fastmcp_server):
        """Test that the calculator tool registers correctly."""
        # Call the register function
        register(fastmcp_server)
        
        # Verify the function was registered
        assert 'calculator' in fastmcp_server._registered_functions
        
        # Verify it was added to the tool manager
        assert hasattr(fastmcp_server, '_tool_manager')
        tool_manager = fastmcp_server._tool_manager
        assert 'calculator' in tool_manager._tools
        
        # Verify tool method was called once
        assert fastmcp_server.tool.call_count == 1
    
    @pytest.mark.asyncio
    async def test_response_format(self):
        """Test that all responses follow the expected format."""
        # Success response
        result = await calculator("add", 1, 2)
        assert isinstance(result, dict)
        assert "result" in result
        assert "description" in result
        assert "status" in result
        assert result["status"] == "success"
        
        # Error response
        result = await calculator("invalid", 1, 2)
        assert isinstance(result, dict)
        assert "error" in result
        assert "status" in result
        assert result["status"] == "error"
        assert "result" not in result
    
    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Test edge cases like very small numbers and zero."""
        # Zero operations
        result = await calculator("add", 0, 0)
        assert result["result"] == 0
        
        result = await calculator("multiply", 5, 0)
        assert result["result"] == 0
        
        # Very small numbers
        result = await calculator("add", 0.000001, 0.000002)
        assert abs(result["result"] - 0.000003) < 1e-10
        
        # Division resulting in float
        result = await calculator("divide", 1, 3)
        assert abs(result["result"] - 0.3333333333333333) < 1e-10 