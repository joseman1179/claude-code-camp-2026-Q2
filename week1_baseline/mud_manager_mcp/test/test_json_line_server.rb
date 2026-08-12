# frozen_string_literal: true

require_relative "helper"

class TestJsonLineServer < Minitest::Test
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
    MudManagerMcp::JsonLineServer.new(dispatcher: @dispatcher, pool: @pool)
  end

  def test_connect_login_send_roundtrip
    msgs = run_server(server, [
      %({"id":1,"op":"connect"}),
      %({"id":2,"op":"login"}),
      %({"id":3,"op":"send","raw":"look"})
    ])
    assert_equal true, msgs[0]["ok"]
    assert_equal true, msgs[1]["ok"]
    assert_match(/You do: look/, msgs[2]["text"])
  end

  def test_send_without_connect_logs_in_lazily
    msgs = run_server(server, [%({"id":1,"op":"send","raw":"look"})])
    assert_match(/You do: look/, msgs[0]["text"])
  end

  def test_unknown_op_is_an_error
    msgs = run_server(server, [%({"id":1,"op":"bogus"})])
    assert_equal false, msgs[0]["ok"]
    assert_match(/unknown op/, msgs[0]["error"])
  end
end
