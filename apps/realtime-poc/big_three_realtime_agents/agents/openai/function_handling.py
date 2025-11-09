"""Function call handling for OpenAI Realtime Agent."""

import json
import logging
from typing import Dict, Any


class FunctionHandler:
    """Handles function call execution for OpenAI Realtime Agent."""

    def __init__(
        self,
        logger: logging.Logger,
        agent_tools,
        browser_tools,
        filesystem_tools,
        reporting_tools,
        ui_logger,
    ):
        self.logger = logger
        self.agent_tools = agent_tools
        self.browser_tools = browser_tools
        self.filesystem_tools = filesystem_tools
        self.reporting_tools = reporting_tools
        self.ui_logger = ui_logger

        self.current_function_calls = {}

    def handle_function_call_delta(self, event: Dict[str, Any]):
        """Handle incremental function call arguments."""
        call_id = event.get("call_id")
        delta = event.get("delta", "")

        if call_id not in self.current_function_calls:
            self.current_function_calls[call_id] = {
                "name": event.get("name", ""),
                "arguments": "",
            }

        self.current_function_calls[call_id]["arguments"] += delta

    def handle_response_done(self, event: Dict[str, Any], ws):
        """Handle response.done event - execute all function calls."""
        response = event.get("response", {})
        output_items = response.get("output", [])

        for item in output_items:
            if item.get("type") == "function_call":
                call_id = item.get("call_id")
                name = item.get("name")
                arguments_str = item.get("arguments", "{}")

                self.logger.info(f"Executing function: {name}")
                self.ui_logger(name, call_id, arguments_str)

                # Execute tool call
                output = self.execute_tool_call(name, arguments_str)

                # Send result back
                self.send_function_output(ws, call_id, output)

        # Clear function calls
        self.current_function_calls = {}

    def execute_tool_call(self, tool_name: str, arguments_json: str) -> str:
        """Execute a tool call and return JSON output."""
        try:
            args = json.loads(arguments_json)
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error": "Invalid JSON arguments"})

        try:
            # Route to appropriate tool handler
            if tool_name == "list_agents":
                result = self.agent_tools.list_agents()
            elif tool_name == "create_agent":
                result = self.agent_tools.create_agent(**args)
            elif tool_name == "command_agent":
                result = self.agent_tools.command_agent(**args)
            elif tool_name == "check_agent_result":
                result = self.agent_tools.check_agent_result(**args)
            elif tool_name == "delete_agent":
                result = self.agent_tools.delete_agent(**args)
            elif tool_name == "browser_use":
                result = self.browser_tools.browser_use(**args)
            elif tool_name == "open_file":
                result = self.filesystem_tools.open_file(**args)
            elif tool_name == "read_file":
                result = self.filesystem_tools.read_file(**args)
            elif tool_name == "report_costs":
                result = self.reporting_tools.report_costs()
            else:
                result = {"ok": False, "error": f"Unknown tool: {tool_name}"}

            return json.dumps(result, ensure_ascii=False)

        except Exception as exc:
            self.logger.exception(f"Tool execution error: {tool_name}")
            return json.dumps({"ok": False, "error": str(exc)})

    def send_function_output(self, ws, call_id: str, output_payload: str):
        """Send function call output back to OpenAI."""
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": output_payload,
            },
        }
        ws.send(json.dumps(event))

        # Request next response
        response_event = {"type": "response.create", "response": {}}
        ws.send(json.dumps(response_event))
        self.logger.info(f"Sent function output for call_id={call_id}")
