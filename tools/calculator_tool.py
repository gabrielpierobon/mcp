from typing import Dict, Any

async def calculator(operation: str, num1: float, num2: float) -> Dict[str, Any]:
    """
    Perform basic arithmetic operations (add, subtract, multiply, divide).
    
    Args:
        operation: The operation to perform - "add", "subtract", "multiply", "divide"
        num1: The first number
        num2: The second number
        
    Returns:
        Dict containing the result and a description of the operation performed
    """
    print(f"INFO: Calculator tool called with operation: {operation}, numbers: {num1}, {num2}")
    
    operation = operation.lower().strip()
    result = None
    
    try:
        if operation == "add" or operation == "+":
            result = num1 + num2
            description = f"{num1} + {num2} = {result}"
        elif operation == "subtract" or operation == "-":
            result = num1 - num2
            description = f"{num1} - {num2} = {result}"
        elif operation == "multiply" or operation == "*":
            result = num1 * num2
            description = f"{num1} × {num2} = {result}"
        elif operation == "divide" or operation == "/":
            if num2 == 0:
                return {
                    "error": "Division by zero is not allowed",
                    "status": "error"
                }
            result = num1 / num2
            description = f"{num1} ÷ {num2} = {result}"
        else:
            return {
                "error": f"Unknown operation: {operation}. Please use 'add', 'subtract', 'multiply', or 'divide'",
                "status": "error"
            }
        
        return {
            "result": result,
            "description": description,
            "status": "success"
        }
    except Exception as e:
        print(f"ERROR: Calculator operation failed: {str(e)}")
        return {
            "error": f"Calculation error: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    mcp_instance.tool()(calculator) 