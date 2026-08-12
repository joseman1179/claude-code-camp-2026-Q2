require "json"
require_relative "base"

module Boukensha
  module Backends
    class DeepSeek < Base
      BASE_URL = "https://api.deepseek.com/v1/chat/completions"
      MODELS = {
        "deepseek-chat" => {
          context_window: 128_000,
          cost_per_million: { input: 0.27, output: 1.10 },
          usage_unit: :tokens
        },
        "deepseek-reasoner" => {
          context_window: 128_000,
          cost_per_million: { input: 0.55, output: 2.19 },
          usage_unit: :tokens
        },
        "deepseek-v4-pro" => {
          context_window: 256_000,
          cost_per_million: { input: 0.50, output: 2.00 },
          usage_unit: :tokens
        }
      }.freeze

      def initialize(api_key:, model:)
        @api_key = api_key
        configure_model(model)
      end

      def to_messages(system, messages)
        system_message = [{ role: "system", content: system }]
        conversation   = messages.map do |msg|
          case msg.role
          when :tool_result
            { role: "tool", tool_call_id: msg.tool_use_id, content: msg.content }
          when :assistant
            assistant_message(msg.content)
          else
            { role: msg.role.to_s, content: msg.content }
          end
        end
        system_message + conversation
      end

      def to_tools(tools)
        tools.values.map do |tool|
          {
            type: "function",
            function: {
              name: tool.name,
              description: tool.description,
              parameters: {
                type: "object",
                properties: tool.parameters,
                required: tool.parameters.keys.map(&:to_s)
              }
            }
          }
        end
      end

      def to_payload(context, max_output_tokens: 1024, tools: nil)
        {
          model: @model,
          messages: to_messages(context.system, context.messages),
          tools: tools.nil? ? to_tools(context.tools) : tools,
          max_tokens: max_output_tokens
        }
      end

      def headers
        {
          "Content-Type"  => "application/json",
          "Authorization" => "Bearer #{@api_key}"
        }
      end

      def url
        BASE_URL
      end

      def parse_response(response)
        message    = response.dig("choices", 0, "message") || {}
        tool_calls = message["tool_calls"] || []

        content = []
        content << { "type" => "text", "text" => message["content"] } if message["content"]

        tool_calls.each do |tc|
          content << {
            "type"  => "tool_use",
            "id"    => tc["id"],
            "name"  => tc.dig("function", "name"),
            "input" => JSON.parse(tc.dig("function", "arguments") || "{}")
          }
        end

        { stop_reason: tool_calls.empty? ? "end_turn" : "tool_use", content: content }
      end

      private

      def assistant_message(content)
        blocks = content.is_a?(String) ? [{ "type" => "text", "text" => content }] : content

        text_blocks = blocks.select { |b| b["type"] == "text" }
        tool_blocks = blocks.select { |b| b["type"] == "tool_use" }

        message = { role: "assistant", content: text_blocks.map { |b| b["text"] }.join }
        unless tool_blocks.empty?
          message[:tool_calls] = tool_blocks.map do |b|
            {
              id: b["id"],
              type: "function",
              function: { name: b["name"], arguments: b["input"].to_json }
            }
          end
        end
        message
      end
    end
  end
end
