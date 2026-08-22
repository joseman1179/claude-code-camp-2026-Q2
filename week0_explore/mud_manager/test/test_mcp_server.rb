# frozen_string_literal: true

require_relative "helper"

# Drives McpServer directly over StringIO against a real FakeMud-backed
# SessionPool — the full MCP handshake and dispatch path, in-process.
class TestMcpServer < Minitest::Test
  include MudManagerMcpTestHelper

  def setup
    @fake = MudManagerMcp::FakeMud.new
    @pool = MudManagerMcp::SessionPool.new(config_for(@fake))
    @dispatcher = MudManagerMcp::Dispatcher.new(@pool)
  end

  def teardown
    @pool.close
    @fake.stop
  end

  def server
    MudManagerMcp::McpServer.new(dispatcher: @dispatcher)
  end

  def test_initialize_reports_server_info
    msgs = run_server(server, [
      %({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}})
    ])
    assert_equal "mud-manager", msgs.first["result"]["serverInfo"]["name"]
    refute_nil msgs.first["result"]["serverInfo"]["version"]
  end

  def test_tools_list_returns_26_tools
    msgs = run_server(server, [%({"jsonrpc":"2.0","id":1,"method":"tools/list"})])
    assert_equal 26, msgs.first["result"]["tools"].size
  end

  def test_tools_call_look
    msgs = run_server(server, [
      %({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"look","arguments":{}}})
    ])
    result = msgs.first["result"]
    assert_equal false, result["isError"]
    assert_match(/You do: look/, result["content"][0]["text"])
  end

  def test_tools_call_attack_defaults_style
    msgs = run_server(server, [
      %({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"attack","arguments":{"target":"dragon"}}})
    ])
    assert_match(/You do: kill dragon/, msgs.first["result"]["content"][0]["text"])
  end

  def test_tool_error_comes_back_as_data
    msgs = run_server(server, [
      %({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"move","arguments":{"direction":"sideways"}}})
    ])
    result = msgs.first["result"]
    assert result["isError"]
    assert_match(/argument_error/, result["content"][0]["text"])
  end

  def test_unknown_method_is_a_jsonrpc_error
    msgs = run_server(server, [%({"jsonrpc":"2.0","id":1,"method":"bogus"})])
    assert_equal(-32601, msgs.first["error"]["code"])
  end
end
