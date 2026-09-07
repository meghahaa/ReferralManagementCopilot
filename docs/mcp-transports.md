# MCP Transports & Interoperability Architecture

This document describes the transport mechanisms and adapter integration for the custom Model Context Protocol (MCP) server.

---

## 1. Supported MCP Transports

The MCP server implemented in [server.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/mcp/server.py) supports two primary transport layers:

1. **`stdio` Transport (Default for local CLI/Agent execution)**:
   - Standard Input / Output JSON-RPC stream.
   - Used for zero-overhead local process communication between the LangGraph agent host and the MCP server process.

2. **`SSE / HTTP` Transport (Production Remote Integration)**:
   - Server-Sent Events over HTTP using `sse-starlette` and `uvicorn`.
   - Used when exposing healthcare tools across separate microservice containers.

---

## 2. Adapter Layer Integration

The agent host consumes MCP tools through `langchain-mcp-adapters` wrapped in [client.py](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/src/referral_copilot/mcp/client.py):
```python
# Invocation Pattern
mcp_client = MCPClientAdapter()
result = mcp_client.invoke_eligibility_check(patient_id="PAT-001")
```

All invocations generate committed audit logs in [evidence/AC-10_mcp_invocation.json](file:///home/megha/Documents/Virtusa/Capstone2/ReferralManagementCopilot/evidence/AC-10_mcp_invocation.json).
