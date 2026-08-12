# frozen_string_literal: true

module MudManagerMcp
  # Turns a (tool name, JSON arguments) pair into [text, is_error]. Tool-level
  # failures — bad arguments, a dropped connection — are returned as data, not
  # raised, so the calling agent loop can keep going. Only truly unknown tools
  # or daemon misconfiguration should surprise the caller.
  class Dispatcher
    def initialize(pool)
      @pool = pool
    end

    def call(name, arguments = {})
      arguments ||= {}

      # Daemon additions rather than MUD verbs.
      case name.to_s
      when "poll"      then return [@pool.drain_async, false]
      when "mud_status" then return [@pool.status, false]
      end

      spec = Spec.find(name)
      return ["unknown tool: #{name}", true] unless spec

      command = spec.build(arguments)
      [@pool.execute(command), false]
    rescue ArgumentError => e
      ["argument_error: #{e.message}", true]
    rescue MudManager::Session::ConnectionError,
           MudManager::Session::LoginError,
           MudManager::Session::Timeout => e
      ["session error: #{e.message}", true]
    rescue MudManagerMcp::Error => e
      ["error: #{e.message}", true]
    end
  end
end
