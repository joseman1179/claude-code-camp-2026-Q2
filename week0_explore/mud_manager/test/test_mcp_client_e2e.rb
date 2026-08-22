# frozen_string_literal: true

require_relative "helper"

# The real end-to-end path: spawn bin/mud-manager --mcp as a subprocess and
# drive it with the daemon's own stdio client against a FakeMud.
class TestMcpClientE2e < Minitest::Test
  def setup
    @fake = MudManagerMcp::FakeMud.new
  end

  def teardown
    @client&.close
    @fake&.stop
  end

  def spawn_client
    @client = MudManagerMcp::McpClient.spawn(
      command: RbConfig.ruby, args: [MUD_MANAGER_BIN, "--mcp"],
      env: {
        "MUD_HOST"     => @fake.host,
        "MUD_PORT"     => @fake.port.to_s,
        "MUD_NAME"     => "Gandalf",
        "MUD_PASSWORD" => "secret"
      }
    )
  end

  def test_handshake_and_tool_discovery
    client = spawn_client
    assert_equal "mud-manager", client.server_info["name"]
    refute_nil client.server_info["version"]
    assert_equal 26, client.tools.size
  end

  def test_call_tool_reaches_the_mud
    client = spawn_client
    assert_match(/You do: look/, client.call_tool("look")[:text])
    assert_match(/You do: kill dragon/, client.call_tool("attack", "target" => "dragon")[:text])
  end

  def test_tool_error_comes_back_as_data
    client = spawn_client
    result = client.call_tool("move", "direction" => "sideways")
    assert result[:error]
    assert_match(/argument_error/, result[:text])
  end

  def test_spawning_a_nonexistent_command_raises
    assert_raises(Errno::ENOENT) do
      MudManagerMcp::McpClient.spawn(command: "mud-manager-no-such-binary-xyz")
    end
  end
end
