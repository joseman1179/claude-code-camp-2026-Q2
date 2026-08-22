# frozen_string_literal: true

require "socket"

module MudManagerMcp
  # A minimal in-memory CircleMUD stand-in for tests and dry runs. It speaks
  # just enough of the telnet login + prompt protocol for MudManager::Session
  # to connect and drive it: ask for a name, ask for a password, print a
  # Welcome line, then echo every command as "You do: <command>" terminated by
  # the "> " prompt sentinel. It deliberately exercises the full login dance so
  # the daemon's lazy connect/login path is covered, not bypassed.
  class FakeMud
    attr_reader :host, :port

    def initialize(host: "127.0.0.1", port: 0)
      @host    = host
      @server  = TCPServer.new(host, port)
      @port    = @server.addr[1]
      @clients = []
      @threads = []
      @thread  = Thread.new { accept_loop }
      @thread.report_on_exception = false
    end

    def stop
      @server.close rescue nil
      @clients.each { |c| c.close rescue nil }
      @threads.each { |t| t.kill rescue nil }
      @thread.kill rescue nil
    end

    private

    def accept_loop
      loop do
        sock = @server.accept
        @clients << sock
        t = Thread.new(sock) { |s| handle_client(s) }
        t.report_on_exception = false
        @threads << t
      end
    rescue IOError, Errno::EBADF, Errno::EINVAL
      # server closed — done
    end

    def handle_client(sock)
      sock.write("By what name do you wish to be known? ")
      name = sock.gets&.strip
      sock.write("Password: ")
      sock.gets&.strip
      sock.write("Welcome, #{name}. \r\n> ")

      while (line = sock.gets)
        cmd = line.strip
        if cmd.empty?
          sock.write("> ")
        elsif cmd == "1"
          sock.write("\r\n> ")
        else
          sock.write("You do: #{cmd}\r\n> ")
        end
      end
    rescue IOError, Errno::ECONNRESET, Errno::EPIPE, Errno::ECONNABORTED
      # client disconnected
    ensure
      sock.close rescue nil
    end
  end
end
