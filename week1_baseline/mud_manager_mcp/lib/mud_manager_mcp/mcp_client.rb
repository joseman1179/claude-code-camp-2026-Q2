# frozen_string_literal: true

require "open3"
require "json"

module MudManagerMcp
  # A minimal MCP-over-stdio client, kept test-scoped inside the daemon's own
  # package for its end-to-end suite. The daemon must not depend on boukensha
  # (it serves five language tracks), so it carries its own ~60-line client
  # rather than reaching across packages. Boukensha's copy is canonical for
  # boukensha; this one exists so the daemon can be exercised standalone.
  class McpClient
    class Error < StandardError; end

    PROTOCOL_VERSION = "2025-06-18"

    attr_reader :server_info, :tools

    def self.spawn(command:, args: [], env: {})
      new(command: command, args: args, env: env)
    end

    def initialize(command:, args: [], env: {})
      cmd = [command.to_s, *Array(args).map(&:to_s)]
      env = env.each_with_object({}) { |(k, v), h| h[k.to_s] = v.to_s }
      @stdin, @stdout, @stderr, @wait = Open3.popen3(env, *cmd)
      @id = 0
      handshake
      @tools = fetch_tools
    end

    # Call a tool. Returns { text:, error: (bool) }.
    def call_tool(name, arguments = {})
      res = request("tools/call", { "name" => name.to_s, "arguments" => arguments })
      result = res["result"] or raise Error, "tools/call error: #{res["error"].inspect}"
      text = Array(result["content"]).map { |c| c["text"] }.compact.join("\n")
      { text: text, error: !!result["isError"] }
    end

    def close
      @stdin.close rescue nil
      @wait&.value
      @stdout.close rescue nil
      @stderr.close rescue nil
    end

    private

    def handshake
      res = request("initialize", {
        "protocolVersion" => PROTOCOL_VERSION,
        "capabilities"    => {},
        "clientInfo"      => { "name" => "mud-manager-e2e", "version" => MudManagerMcp::VERSION }
      })
      @server_info = res.dig("result", "serverInfo")
      notify("notifications/initialized")
    end

    def fetch_tools
      request("tools/list").dig("result", "tools") || []
    end

    def request(method, params = {})
      id = (@id += 1)
      write({ "jsonrpc" => "2.0", "id" => id, "method" => method, "params" => params })
      read_until(id)
    end

    def notify(method, params = {})
      write({ "jsonrpc" => "2.0", "method" => method, "params" => params })
    end

    def write(obj)
      @stdin.puts(JSON.generate(obj))
      @stdin.flush
    end

    def read_until(id)
      loop do
        line = @stdout.gets
        raise Error, "server closed the connection" if line.nil?

        line = line.strip
        next if line.empty?

        msg = JSON.parse(line)
        return msg if msg["id"] == id
        # ignore server-initiated notifications / mismatched ids
      end
    end
  end
end
