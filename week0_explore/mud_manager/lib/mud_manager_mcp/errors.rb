# frozen_string_literal: true

module MudManagerMcp
  # Base error for the daemon package. Session-level failures (connection,
  # login, timeout) stay on MudManager::Session; everything raised by this
  # package itself descends from here so callers can distinguish "the MUD
  # broke" from "we misconfigured the daemon".
  class Error < StandardError; end

  # The peer sent something that isn't a well-formed JSON-RPC / JSON-line
  # request. Recoverable per-message; the server keeps running.
  class ProtocolError < Error; end

  # Missing credentials, bad port, or any other reason the daemon cannot
  # start a session. Raised before the socket is touched.
  class ConfigurationError < Error; end
end
