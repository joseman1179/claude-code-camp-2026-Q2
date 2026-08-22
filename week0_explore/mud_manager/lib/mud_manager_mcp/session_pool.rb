# frozen_string_literal: true

require "mud_manager"

module MudManagerMcp
  # Owns the daemon's MudManager::Session. Exactly one session per process
  # (the stdio transport's "credentials by environment" convention gives us
  # one character), created lazily on the first command and kept open for the
  # server's whole lifetime. Connect, login, and the login dance all happen
  # behind this boundary — the LLM never sees a socket or a credential.
  class SessionPool
    def initialize(config)
      @config    = config
      @session   = nil
      @logged_in = false
    end

    def connected?
      !@session.nil? && @session.open?
    end

    # Open (or replace) the underlying telnet session. No login yet.
    def connect(host: nil, port: nil)
      close
      @session = MudManager::Session.new(host: host || @config.host, port: port || @config.port)
      @session.open
      @logged_in = false
      self
    end

    # Run the multi-step login dance against the open session.
    def login(name: nil, password: nil)
      session = @session or raise MudManagerMcp::Error, "not connected — call connect first"
      session.login(name || @config.name, password || @config.password)
      @logged_in = true
      self
    end

    # High-level "run a command": drain stale bytes, send, collect until the
    # prompt. Used by the MCP dispatcher and the raw JSON-line "send" op.
    def execute(command)
      session = ensure_session
      session.drain
      session.send_command(command)
      session.read_until_prompt
    end

    def read_prompt(timeout: nil)
      ensure_session.read_until_prompt(timeout: timeout)
    end

    # Async chatter that arrived between commands (combat, tells, room events).
    def drain_async
      return "(not connected)" unless connected?

      text = @session.drain
      text.empty? ? "(no pending output)" : text
    end

    def status
      return "not connected" unless connected?

      @logged_in ? "connected and logged in as #{@config.name}" : "connected (not logged in)"
    end

    def close
      @session&.close
      @session   = nil
      @logged_in = false
    end

    private

    # Lazy connect + login on first use. Credentials must be present; the
    # daemon refuses to invent them.
    def ensure_session
      return @session if connected?

      unless @config.credentials?
        raise MudManagerMcp::ConfigurationError, "no MUD credentials (set MUD_NAME and MUD_PASSWORD)"
      end

      connect
      login
      @session
    end
  end
end
