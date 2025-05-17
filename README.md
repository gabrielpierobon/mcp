# MCP Server for n8n Integration

This project implements a Model Context Protocol (MCP) server designed to work seamlessly with your local n8n server. The MCP server enables AI agents to interact with your n8n workflows and tools through a standardized protocol.

## Overview

The Model Context Protocol (MCP) is a specification that allows AI agents to interact with external tools and services. This implementation specifically focuses on integrating with n8n, a powerful workflow automation platform, allowing AI agents to:

- Execute n8n workflows
- Access n8n tools and functions
- Interact with your automation workflows through a standardized interface

## Features

- MCP server implementation compatible with n8n
- Support for SSE (Server-Sent Events) endpoint
- Authentication support (Bearer and generic header methods)
- Tool selection and filtering capabilities
- Integration with local n8n server

## Getting Started

1. Clone this repository
2. Set up your Python virtual environment
3. Install dependencies
4. Configure your n8n server connection
5. Start the MCP server

## Integration with n8n

This MCP server works with the n8n MCP Client Tool node, which allows you to:
- Connect to external MCP servers
- Expose specific tools to AI agents
- Control which tools are available to your AI workflows
- Manage authentication and security

## Documentation

For more information about the Model Context Protocol and n8n integration, refer to:
- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [n8n MCP Client Tool Documentation](https://docs.n8n.io/integrations/builtin/cluster-nodes/n8n-nodes-base.mcpClientTool/)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 