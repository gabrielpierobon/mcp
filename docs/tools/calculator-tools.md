# Calculator Tools Documentation

Tools for performing basic arithmetic operations with error handling and validation.

## Overview

The Calculator tools provide AI agents with reliable arithmetic computation capabilities for mathematical operations and calculations.

## Installation Requirements

No external dependencies required. Uses built-in Python functionality.

## Environment Variables

None required.

## Available Functions

### `calculator`

Performs basic arithmetic operations with comprehensive error handling.

**What it does:**
- Executes fundamental mathematical operations
- Validates input parameters and operation types
- Handles division by zero and other mathematical errors
- Returns formatted results with operation descriptions
- Supports both word and symbol operation formats

**Parameters:**
- `operation` (required) - Operation type: "add"/"+" "subtract"/"-", "multiply"/"*", "divide"/"/"
- `num1` (required) - First number (float)
- `num2` (required) - Second number (float)

**Returns:**
- Calculation result as a number
- Human-readable operation description
- Error messages for invalid operations
- Status indicators for success/failure

## Supported Operations

- **Addition**: "add" or "+"
- **Subtraction**: "subtract" or "-"
- **Multiplication**: "multiply" or "*"
- **Division**: "divide" or "/"

## Use Cases

- Mathematical computations in workflows
- Financial calculations and conversions
- Data analysis and statistical operations
- Engineering and scientific calculations
- Educational mathematical demonstrations

## Error Handling

- Division by zero protection
- Invalid operation type detection
- Input validation for numeric parameters
- Comprehensive error reporting with helpful messages