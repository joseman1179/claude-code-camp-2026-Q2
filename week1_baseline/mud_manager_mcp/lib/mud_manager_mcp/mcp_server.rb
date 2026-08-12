# frozen_string_literal: true

require "json"

module MudManagerMcp
  # A minimal MCP (Model Context Protocol) server over stdio: JSON-RPC 2.0,
  # one JSON object per line. It implements exactly the three methods an MCP
  # host needs to drive the daemon — initialize, tools/list, tools/call — plus
  # the notifications/initialized acknowledgement. Tool-level failures are
  # returned as `isError: true` content, never as a JSON-RPC error (those are
  # reserved for protocol problems), so an agent loop survives a bad move.
  class McpServer
    PROTOCOL_VERSION = "2025-06-18"
    SERVER_NAME      = "mud-manager"

    def initialize(dispatcher:, input: $stdin, output: $stdout)
      @dispatcher = dispatcher
      @input      = input
      @output     = output
    end

    def run
      while (line = @input.gets)
        line = line.strip
        next if line.empty?

        begin
          msg = JSON.parse(line)
        rescue JSON::ParserError
          write(jsonrpc_error(nil, -32700, "parse error"))
          next
        end

        response = handle(msg)
        write(response) if response
      end
    end

    private

    def handle(msg)
      id     = msg["id"]
      method = msg["method"]

      case method
      when "initialize"
        jsonrpc_result(id, {
          "protocolVersion" => PROTOCOL_VERSION,
          "capabilities"    => {},
          "serverInfo"      => { "name" => SERVER_NAME, "version" => MudManagerMcp::VERSION }
        })
      when "tools/list"
        jsonrpc_result(id, { "tools" => Spec.tools.map(&:to_mcp_tool) })
      when "tools/call"
        params = msg["params"] || {}
        name   = params["name"]
        args   = params["arguments"] || {}
        text, is_error = @dispatcher.call(name, args)
        jsonrpc_result(id, {
          "content" => [{ "type" => "text", "text" => text }],
          "isError" => is_error
        })
      when "notifications/initialized", "notifications/cancelled"
        nil # notification — no response
      else
        jsonrpc_error(id, -32601, "method not found: #{method}")
      end
    end

    def jsonrpc_result(id, result)
      { "jsonrpc" => "2.0", "id" => id, "result" => result }
    end

    def jsonrpc_error(id, code, message)
      { "jsonrpc" => "2.0", "id" => id, "error" => { "code" => code, "message" => message } }
    end

    def write(obj)
      @output.puts(JSON.generate(obj))
      @output.flush
    end
  end
end
