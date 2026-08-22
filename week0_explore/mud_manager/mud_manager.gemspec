Gem::Specification.new do |spec|
  spec.name        = "mud_manager"
  spec.version     = "0.2.0"
  spec.summary     = "MudManager — CircleMUD session, command primitives, and the mud-manager MCP daemon"
  spec.description = "Provides MudManager::Session (a long-lived telnet connection with " \
                     "background buffering and IAC stripping), MudManager::Primitives " \
                     "(a stateless library of typed CircleMUD command builders), and the " \
                     "mud-manager MCP daemon that exposes both as tools over stdio for " \
                     "agents in any language."
  spec.authors     = ["Andrew Brown"]
  spec.email       = ["andrew@exampro.co"]
  spec.license     = "MIT"

  spec.required_ruby_version = ">= 3.0"

  spec.files       = Dir["lib/**/*.rb"] + ["bin/mud-manager", "primitives.json", "README.md"]
  spec.bindir      = "bin"
  spec.executables = ["mud-manager"]

  # No external dependencies — socket, thread, json, open3, optparse are stdlib.
end
