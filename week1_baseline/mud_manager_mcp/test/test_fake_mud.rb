# frozen_string_literal: true

require_relative "helper"

# The FakeMud must exercise the real MudManager::Session login dance, not a
# shortcut — that's what makes it a useful stand-in for the daemon tests.
class TestFakeMud < Minitest::Test
  def test_session_login_and_echo_roundtrip
    fake = MudManagerMcp::FakeMud.new
    session = MudManager::Session.new(host: fake.host, port: fake.port)
    session.open
    session.login("Gandalf", "secret")

    session.send_command("look")
    assert_match(/You do: look/, session.read_until_prompt)
  ensure
    session&.close
    fake&.stop
  end

  def test_attack_echoes_the_raw_command
    fake = MudManagerMcp::FakeMud.new
    session = MudManager::Session.new(host: fake.host, port: fake.port)
    session.open
    session.login("Gandalf", "secret")

    session.send_command(MudManager::Primitives.attack("kill", "dragon"))
    assert_match(/You do: kill dragon/, session.read_until_prompt)
  ensure
    session&.close
    fake&.stop
  end
end
