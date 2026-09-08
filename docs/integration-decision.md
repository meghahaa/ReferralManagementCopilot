# Architectural Integration Decision Writeup

This document documents the architectural rationale behind choosing Model Context Protocol (MCP) over direct custom REST APIs, Direct DB Access, or Agent-to-Agent (A2A) protocols.

---

## 1. Trade-Off Analysis

| Integration Pattern | Interoperability | Security & Isolation | Standard Tool Interface | Overhead | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Model Context Protocol (MCP)** | High (Standard JSON-RPC over stdio/HTTP) | High (Decoupled tool boundaries) | High (`langchain-mcp-adapters`) | Low | **SELECTED** |
| **Direct Custom REST APIs** | Medium (Requires custom HTTP wrappers) | Medium | Medium | Medium | Rejected |
| **Direct Database Access** | Low (Tight coupling to DB schema) | Low (Bypasses application authorization) | Low | Low | Rejected |
| **Agent-to-Agent (A2A) Custom Protocol** | Low (Custom message passing) | Medium | Low | High | Rejected |

---

## 2. Selection Rationale for MCP

1. **Standardized Tooling**: MCP provides a unified specification for tools and resources, allowing any agent framework (LangGraph, AutoGen, CrewAI) to consume healthcare data sources seamlessly.
2. **Schema & Validation**: MCP server definitions automatically expose typed input schemas, simplifying validation at tool invocation boundaries.
3. **Decoupled Architecture**: The MCP server in [server.py](../src/referral_copilot/mcp/server.py) runs as an independent component, protecting sensitive healthcare lookups behind clean API contracts.
