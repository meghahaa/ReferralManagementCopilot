# MCP Transports & Interoperability Architecture

This document describes the transport mechanisms and adapter integration for the custom Model Context Protocol (MCP) server.

---

## 1. Supported MCP Transports

The MCP server implemented in [server.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/mcp/server.py) supports two primary transport layers:

1. **`stdio` Transport (Default for local CLI/Agent execution)**:
   - Standard Input / Output JSON-RPC stream.
   - Used for zero-overhead local process communication between the LangGraph agent host and the MCP server process.

Remote SSE/HTTP transport is not currently implemented. The supported and tested
transport is local stdio; remote deployment would require a separate MCP HTTP
server and authentication design.

---

## 2. Adapter Layer Integration

The agent host consumes MCP tools through `langchain-mcp-adapters` wrapped in [client.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/mcp/client.py). The adapter launches the custom server as a separate stdio process for every tool session:
```python
# Invocation Pattern
mcp_client = MCPClientAdapter()
result = mcp_client.invoke_eligibility_check(patient_id="PAT-001")
```

All invocations generate committed audit logs in [evidence/AC-10_mcp_invocation.json](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evidence/AC-10_mcp_invocation.json).

The repository also contains a raw MCP SDK compatibility path because the bundled offline SDK may be older than the installed adapter package. This fallback still performs MCP initialization and JSON-RPC tool/resource calls over stdio; it does not import or call server tool functions directly.
