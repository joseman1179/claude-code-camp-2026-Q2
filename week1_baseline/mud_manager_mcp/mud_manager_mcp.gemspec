# frozen_string_literal: true

require_relative "lib/mud_manager_mcp/version"

Gem::Specification.new do |spec|
  spec.name        = "mud_manager_mcp"
  spec.version     = MudManagerMcp::VERSION
  spec.summary     = "mud-manager MCP daemon — MudManager sessions and primitives over Model Context Protocol"
  spec.description = "Exposes MudManager::Session (a long-lived telnet connection) and " \
                     "MudManager::Primitives (typed CircleMUD command builders) as an MCP " \
                     "server over stdio, so agents in any language can play the MUD without " \
                     "touching Ruby or telnet. Also ships a raw JSON-line protocol mode."
  spec.authors     = ["Andrew Brown"]
  spec.email       = ["andrew@exampro.co"]
  spec.license     = "MIT"

  spec.required_ruby_version = ">= 3.0"

  spec.files       = Dir["lib/**/*.rb"] + ["bin/mud-manager", "primitives.json", "README.md"]
  spec.bindir      = "bin"
  spec.executables = ["mud-manager"]

  # The domain half. See docs/plans/mud_manager/ — the eventual target is a
  # single gem; this split is the intermediate state.
  spec.add_dependency "mud_manager", "~> 0.1"

  # Everything else (socket, json, open3, optparse) is stdlib.
end
