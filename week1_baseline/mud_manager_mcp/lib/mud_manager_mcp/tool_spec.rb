# frozen_string_literal: true

module MudManagerMcp
  # A single MCP tool: its advertised name, description, JSON-Schema input
  # shape, and a builder that turns raw JSON arguments into a command string
  # (or a MudManager::Primitives::Command). Builders may raise ArgumentError
  # for invalid input — the Dispatcher turns that into an isError result.
  class ToolSpec
    attr_reader :name, :description, :properties, :required

    def initialize(name:, description:, properties: {}, required: [], builder:)
      @name        = name
      @description = description
      @properties  = properties
      @required    = required
      @builder     = builder
    end

    # arguments is a String-keyed Hash as it arrives off the JSON-RPC wire.
    def build(arguments = {})
      @builder.call(arguments || {})
    end

    def input_schema
      { "type" => "object", "properties" => properties, "required" => required }
    end

    def to_mcp_tool
      { "name" => name, "description" => description, "inputSchema" => input_schema }
    end
  end
end
