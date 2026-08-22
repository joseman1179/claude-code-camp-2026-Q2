# frozen_string_literal: true

require "minitest/autorun"
require "rbconfig"
require "json"
require "stringio"

MUD_MANAGER_MCP_ROOT = File.expand_path("..", __dir__)
MUD_MANAGER_MCP_LIB  = File.join(MUD_MANAGER_MCP_ROOT, "lib")
MUD_MANAGER_BIN      = File.join(MUD_MANAGER_MCP_ROOT, "bin", "mud-manager")
# Domain lib and daemon lib are the same gem now.
MUD_MANAGER_LIB      = MUD_MANAGER_MCP_LIB

$LOAD_PATH.unshift(MUD_MANAGER_LIB) unless $LOAD_PATH.include?(MUD_MANAGER_LIB)
$LOAD_PATH.unshift(MUD_MANAGER_MCP_LIB) unless $LOAD_PATH.include?(MUD_MANAGER_MCP_LIB)

require "mud_manager"
require "mud_manager_mcp"
require "mud_manager_mcp/fake_mud"
require "mud_manager_mcp/mcp_client"

module MudManagerMcpTestHelper
  # A Config pointed at a given FakeMud.
  def config_for(fake, name: "Gandalf", password: "secret")
    MudManagerMcp::Config.new(env: {
      "MUD_HOST"     => fake.host,
      "MUD_PORT"     => fake.port.to_s,
      "MUD_NAME"     => name,
      "MUD_PASSWORD" => password
    })
  end

  # Drive a server object (McpServer or JsonLineServer) with StringIO pipes and
  # return the JSON objects it wrote back.
  def run_server(server, lines)
    input  = StringIO.new(lines.join("\n") + "\n")
    output = StringIO.new
    server.instance_variable_set(:@input, input)
    server.instance_variable_set(:@output, output)
    server.run
    output.string.lines.map { |l| JSON.parse(l) }
  end
end
