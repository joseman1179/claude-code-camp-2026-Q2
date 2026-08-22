#!/usr/bin/env ruby
# frozen_string_literal: true

# Self-contained smoke test of the daemon: spawn a FakeMud, spawn
# `bin/mud-manager --mcp` as a subprocess, and drive it with the daemon's own
# test client. No live MUD and no API key required.
#
#   ruby examples/boukensha_mcp_demo.rb

require "rbconfig"

$LOAD_PATH.unshift File.expand_path("../lib", __dir__)
$LOAD_PATH.unshift File.expand_path("../../../week0_explore/mud_manager/lib", __dir__)

require "mud_manager_mcp"
require "mud_manager_mcp/fake_mud"
require "mud_manager_mcp/mcp_client"

fake = MudManagerMcp::FakeMud.new
bin  = File.expand_path("../bin/mud-manager", __dir__)

client = MudManagerMcp::McpClient.spawn(
  command: RbConfig.ruby, args: [bin, "--mcp"],
  env: {
    "MUD_HOST"     => fake.host,
    "MUD_PORT"     => fake.port.to_s,
    "MUD_NAME"     => "Gandalf",
    "MUD_PASSWORD" => "secret"
  }
)

puts "server: #{client.server_info.inspect}"
puts "tools:  #{client.tools.size} — #{client.tools.map { |t| t['name'] }.join(', ')}"
puts
puts "look       => #{client.call_tool('look')[:text].inspect}"
puts "attack orc => #{client.call_tool('attack', 'target' => 'orc')[:text].inspect}"
puts "bad cast   => #{client.call_tool('cast_spell', 'spell' => '').inspect}"

client.close
fake.stop

puts "\n[dry run OK — daemon + FakeMud working]"
