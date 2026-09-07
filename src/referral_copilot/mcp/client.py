"""MCP Client Adapter for Referral Copilot.

Satisfies AC-10: Consumes MCP tools/resources and logs structured execution transcripts.
"""

import json
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from referral_copilot.config import settings
from referral_copilot.models.schemas import MCPToolCallRecord


class MCPClientAdapter:
    """Adapter for invoking custom MCP tools and recording evidence transcripts."""

    def __init__(self):
        self.evidence_dir = settings.evidence_dir
        self.server_path = Path(__file__).resolve().parent / "server.py"

    def _connection(self) -> dict:
        child_env = {
            key: value
            for key, value in os.environ.items()
            if key not in {"PS1", "PROMPT_COMMAND"}
        }
        child_env["PYTHONPATH"] = os.pathsep.join([
            str(settings.base_dir / "src"),
            os.environ.get("PYTHONPATH", ""),
        ])
        child_env["MCP_LOG_LEVEL"] = "ERROR"
        return {
            "command": sys.executable,
            "args": [str(self.server_path)],
            "cwd": str(settings.base_dir),
            "env": child_env,
            "transport": "stdio",
        }

    def _invoke(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the domain MCP server over stdio via langchain-mcp-adapters."""
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
        except ImportError:
            return self._invoke_sdk(tool_name, arguments)

        async def call_tool() -> Any:
            client = MultiServerMCPClient({"referral": self._connection()})
            tools = await client.get_tools(server_name="referral")
            tool = next((candidate for candidate in tools if candidate.name == tool_name), None)
            if tool is None:
                raise RuntimeError(f"MCP tool not found: {tool_name}")
            return await tool.ainvoke(arguments)

        result = asyncio.run(call_tool())
        if isinstance(result, str):
            return json.loads(result)
        if isinstance(result, dict):
            return result
        if isinstance(result, list):
            text = "".join(str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in result)
            return json.loads(text)
        raise TypeError(f"Unexpected MCP result type: {type(result).__name__}")

    def _invoke_sdk(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibility path for the pinned vendored MCP SDK."""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def call_tool() -> Any:
            child_env = {
                key: value
                for key, value in os.environ.items()
                if key not in {"PS1", "PROMPT_COMMAND"}
            }
            child_env["PYTHONPATH"] = os.pathsep.join([
                str(settings.base_dir / "src"),
                os.environ.get("PYTHONPATH", ""),
            ])
            child_env["MCP_LOG_LEVEL"] = "ERROR"
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_path)],
                env=child_env,
            )
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    return await session.call_tool(tool_name, arguments)

        result = asyncio.run(call_tool())
        content = getattr(result, "content", result)
        text = "".join(getattr(item, "text", str(item)) for item in content)
        return json.loads(text)

    def invoke_eligibility_check(self, patient_id: str) -> Dict[str, Any]:
        """Invokes MCP tool `eligibility_check`."""
        res_data = self._invoke("eligibility_check", {"patient_id": patient_id})

        record = MCPToolCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tool_name="eligibility_check",
            input_params={"patient_id": patient_id},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def invoke_network_lookup(self, specialty: str) -> Dict[str, Any]:
        """Invokes MCP tool `network_lookup`."""
        res_data = self._invoke("network_lookup", {"specialty": specialty})

        record = MCPToolCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tool_name="network_lookup",
            input_params={"specialty": specialty},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def invoke_specialist_availability(self, specialist_id: str) -> Dict[str, Any]:
        """Invokes MCP tool `specialist_availability`."""
        res_data = self._invoke("specialist_availability", {"specialist_id": specialist_id})

        record = MCPToolCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tool_name="specialist_availability",
            input_params={"specialist_id": specialist_id},
            output_data=res_data,
            ac_id="AC-10"
        )
        self._record_evidence("AC-10_mcp_invocation.json", record)
        return res_data

    def read_cardiology_policy_resource(self) -> str:
        """Invokes MCP resource `referral-policy://cardiology`."""
        async def read_resource() -> str:
            try:
                from langchain_mcp_adapters.client import MultiServerMCPClient
                client = MultiServerMCPClient({"referral": self._connection()})
                async with client.session("referral") as session:
                    result = await session.read_resource("referral-policy://cardiology")
                    return "\n".join(getattr(item, "text", str(item)) for item in result.contents)
            except ImportError:
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client
                child_env = {
                    key: value
                    for key, value in os.environ.items()
                    if key not in {"PS1", "PROMPT_COMMAND"}
                }
                child_env["PYTHONPATH"] = os.pathsep.join([
                    str(settings.base_dir / "src"),
                    os.environ.get("PYTHONPATH", ""),
                ])
                child_env["MCP_LOG_LEVEL"] = "ERROR"
                params = StdioServerParameters(
                    command=sys.executable,
                    args=[str(self.server_path)],
                    env=child_env,
                )
                async with stdio_client(params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        result = await session.read_resource("referral-policy://cardiology")
                        return "\n".join(getattr(item, "text", str(item)) for item in result.contents)

        return asyncio.run(read_resource())

    def _record_evidence(self, filename: str, record: MCPToolCallRecord) -> None:
        """Appends tool invocation record to evidence JSON log."""
        evidence_file = self.evidence_dir / filename
        logs = []
        if evidence_file.exists():
            try:
                with open(evidence_file, "r") as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except Exception:
                logs = []

        logs.append(record.model_dump())
        with open(evidence_file, "w") as f:
            json.dump(logs, f, indent=2)
