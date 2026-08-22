# frozen_string_literal: true

module MudManagerMcp
  # Daemon connection config, read from the process environment. The stdio MCP
  # transport has no "send credentials over the wire" concept, so credentials
  # travel by environment — the same convention every MCP host uses.
  #
  #   MUD_HOST     (default: localhost)
  #   MUD_PORT     (default: 4000)
  #   MUD_NAME     player character name
  #   MUD_PASSWORD player password
  class Config
    attr_reader :host, :port, :name, :password

    def initialize(env: ENV)
      @host     = env["MUD_HOST"] || MudManager::Session::DEFAULT_HOST
      @port     = Integer(env["MUD_PORT"] || MudManager::Session::DEFAULT_PORT)
      @name     = env["MUD_NAME"]
      @password = env["MUD_PASSWORD"]
    end

    def credentials?
      !name.to_s.strip.empty? && !password.to_s.strip.empty?
    end
  end
end
