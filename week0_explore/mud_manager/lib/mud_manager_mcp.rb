# frozen_string_literal: true

require "mud_manager"

require_relative "mud_manager_mcp/version"
require_relative "mud_manager_mcp/errors"
require_relative "mud_manager_mcp/config"
require_relative "mud_manager_mcp/tool_spec"
require_relative "mud_manager_mcp/spec"
require_relative "mud_manager_mcp/session_pool"
require_relative "mud_manager_mcp/dispatcher"
require_relative "mud_manager_mcp/mcp_server"
require_relative "mud_manager_mcp/json_line_server"

# The daemon package: a thin MCP (and raw JSON-line) server over
# MudManager::Session + MudManager::Primitives. The stateful telnet session
# lives here, behind the boundary; foreign-language agents drive it through a
# subprocess. See bin/mud-manager for the executable entry point.
module MudManagerMcp
end
