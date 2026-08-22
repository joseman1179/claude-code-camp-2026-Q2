# frozen_string_literal: true

require "json"

module MudManagerMcp
  # The raw, bespoke JSON-line protocol (--stdio-json). A lower-level escape
  # hatch and teaching artifact: one JSON object per line, with explicit
  # connect/login/send/read_prompt/close ops instead of MCP's tool abstraction.
  #
  #   {"id":1,"op":"connect","host":"localhost","port":4000}
  #   {"id":2,"op":"login","name":"Gandalf","password":"secret"}
  #   {"id":3,"op":"send","raw":"kill goblin"}
  #   {"id":4,"op":"read_prompt","timeout":10}
  #   {"id":5,"op":"close"}
  #
  #   {"id":4,"ok":true,"text":"You hit the goblin.\n> "}
  #   {"id":2,"ok":false,"error":"LoginError: wrong password"}
  class JsonLineServer
    def initialize(dispatcher:, pool:, input: $stdin, output: $stdout)
      @dispatcher = dispatcher
      @pool       = pool
      @input      = input
      @output     = output
    end

    def run
      while (line = @input.gets)
        line = line.strip
        next if line.empty?

        begin
          msg = JSON.parse(line)
        rescue JSON::ParserError => e
          write(id: nil, ok: false, error: "parse error: #{e.message}")
          next
        end

        handle(msg)
      end
    end

    private

    def handle(msg)
      id = msg["id"]
      op = msg["op"]

      case op
      when "connect"
        @pool.connect(host: msg["host"], port: msg["port"])
        write(id: id, ok: true)
      when "login"
        @pool.login(name: msg["name"], password: msg["password"])
        write(id: id, ok: true)
      when "send"
        text = @pool.execute(msg["raw"])
        write(id: id, ok: true, text: text)
      when "read_prompt"
        text = @pool.read_prompt(timeout: msg["timeout"])
        write(id: id, ok: true, text: text)
      when "list_tools"
        write(id: id, ok: true, tools: Spec.tools.map(&:name))
      when "close"
        @pool.close
        write(id: id, ok: true)
      else
        write(id: id, ok: false, error: "unknown op: #{op}")
      end
    rescue MudManager::Session::ConnectionError,
           MudManager::Session::LoginError,
           MudManager::Session::Timeout,
           MudManagerMcp::Error => e
      write(id: msg["id"], ok: false, error: e.message)
    end

    def write(id:, ok:, text: nil, error: nil, tools: nil)
      obj = { "id" => id, "ok" => ok }
      obj["text"]  = text  if text
      obj["error"] = error if error
      obj["tools"] = tools if tools
      @output.puts(JSON.generate(obj))
      @output.flush
    end
  end
end
