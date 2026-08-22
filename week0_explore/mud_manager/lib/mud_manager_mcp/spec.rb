# frozen_string_literal: true

require "json"
require "mud_manager"

module MudManagerMcp
  # Spec is the single source of truth for the daemon's tool surface. It is
  # generated from MudManager::Primitives — the enum tables and command
  # builders are read live, so the MCP schemas cannot drift from the Ruby code
  # they wrap. The same data serializes to primitives.json (see #to_json_spec),
  # the language-neutral spec other tracks can generate from.
  module Spec
    P = MudManager::Primitives

    def self.str(description)
      { "type" => "string", "description" => description }
    end

    def self.enum(values, description:)
      { "type" => "string", "enum" => values, "description" => description }
    end

    def self.present?(value)
      !value.to_s.strip.empty?
    end

    # The 26 tools: 24 gameplay commands plus two daemon additions (poll,
    # mud_status). The two additions have nil builders — the Dispatcher
    # handles them by name, not through a MUD primitive.
    TOOLS = [
      ToolSpec.new(name: "look", description: "Look around your current room.",
                   builder: ->(_a) { P.look }),

      ToolSpec.new(name: "examine", description: "Examine an object or character in detail.",
                   properties: { "target" => str("The object or character to examine.") },
                   required: ["target"],
                   builder: ->(a) { P.examine(a["target"]) }),

      ToolSpec.new(name: "check", description: "Check your character's score and current vitals.",
                   builder: ->(_a) { P.info_self("score") }),

      ToolSpec.new(name: "move", description: "Move one room in a compass direction (or up/down).",
                   properties: { "direction" => enum(P::DIRECTIONS, description: "Compass direction to travel.") },
                   required: ["direction"],
                   builder: ->(a) { P.move(a["direction"]) }),

      ToolSpec.new(name: "flee", description: "Flee from combat.",
                   builder: ->(_a) { P.flee }),

      ToolSpec.new(name: "set_position", description: "Change your body position (stand, sit, rest, sleep, wake).",
                   properties: { "pos" => enum(P::POSITIONS, description: "Body position.") },
                   required: ["pos"],
                   builder: ->(a) { P.set_position(a["pos"]) }),

      ToolSpec.new(name: "track", description: "Track a target through the wilderness.",
                   properties: { "victim" => str("Who to track.") },
                   required: ["victim"],
                   builder: ->(a) { P.track(a["victim"]) }),

      ToolSpec.new(name: "attack", description: "Attack a target with a combat style (defaults to kill).",
                   properties: {
                     "style"  => enum(P::ATTACK_STYLES, description: "Combat style."),
                     "target" => str("Who or what to attack.")
                   },
                   required: ["target"],
                   builder: ->(a) {
                     style = present?(a["style"]) ? a["style"] : "kill"
                     P.attack(style, a["target"])
                   }),

      ToolSpec.new(name: "skill_strike", description: "Use a combat skill against a target (backstab, bash, kick, rescue, assist).",
                   properties: {
                     "skill"  => enum(P::STRIKE_SKILLS, description: "Combat skill."),
                     "target" => str("Who to strike.")
                   },
                   required: %w[skill target],
                   builder: ->(a) { P.skill_strike(a["skill"], a["target"]) }),

      ToolSpec.new(name: "consider", description: "Assess a target's strength relative to yours.",
                   properties: { "target" => str("Who to consider.") },
                   required: ["target"],
                   builder: ->(a) { P.consider(a["target"]) }),

      ToolSpec.new(name: "say", description: "Say something to everyone in the room.",
                   properties: { "text" => str("What to say.") },
                   required: ["text"],
                   builder: ->(a) { P.say_local("say", a["text"]) }),

      ToolSpec.new(name: "tell", description: "Send a private message to another player.",
                   properties: {
                     "target" => str("Player to tell."),
                     "text"   => str("Message text.")
                   },
                   required: %w[target text],
                   builder: ->(a) { P.say_targeted("tell", a["target"], a["text"]) }),

      ToolSpec.new(name: "channel_say", description: "Speak on a public channel (shout, gossip, auction, grats, holler).",
                   properties: {
                     "channel" => enum(P::CHANNELS, description: "Channel to speak on."),
                     "text"    => str("What to say.")
                   },
                   required: %w[channel text],
                   builder: ->(a) { P.say_channel(a["channel"], a["text"]) }),

      ToolSpec.new(name: "get_item", description: "Pick up an object.",
                   properties: { "obj" => str("Object to get.") },
                   required: ["obj"],
                   builder: ->(a) { P.get(a["obj"]) }),

      ToolSpec.new(name: "drop_item", description: "Drop an object from your inventory.",
                   properties: { "obj" => str("Object to drop.") },
                   required: ["obj"],
                   builder: ->(a) { P.drop("drop", a["obj"]) }),

      ToolSpec.new(name: "put_item", description: "Put an object into a container.",
                   properties: {
                     "obj"       => str("Object to put."),
                     "container" => str("Container to put it into.")
                   },
                   required: %w[obj container],
                   builder: ->(a) { P.put(a["obj"], a["container"]) }),

      ToolSpec.new(name: "equip_item", description: "Wear, wield, grab, hold, or remove an item.",
                   properties: {
                     "slot_op" => enum(P::EQUIP_OPS, description: "Equipment operation."),
                     "obj"     => str("Item to equip.")
                   },
                   required: %w[slot_op obj],
                   builder: ->(a) { P.equip(a["slot_op"], a["obj"]) }),

      ToolSpec.new(name: "consume_item", description: "Eat, taste, drink, or sip something.",
                   properties: {
                     "mode" => enum(P::CONSUME_MODES, description: "How to consume it."),
                     "obj"  => str("What to consume.")
                   },
                   required: %w[mode obj],
                   builder: ->(a) { P.consume(a["mode"], a["obj"]) }),

      ToolSpec.new(name: "cast_spell", description: "Cast a spell, optionally at a target.",
                   properties: {
                     "spell"  => str("Spell to cast."),
                     "target" => str("Optional target of the spell.")
                   },
                   required: ["spell"],
                   builder: ->(a) {
                     target = present?(a["target"]) ? a["target"] : nil
                     P.cast(a["spell"], target: target)
                   }),

      ToolSpec.new(name: "use_magic_item", description: "Use, quaff, or recite a magic item.",
                   properties: {
                     "mode" => enum(P::SPELL_ITEM, description: "How to use it."),
                     "item" => str("Item to use.")
                   },
                   required: %w[mode item],
                   builder: ->(a) { P.use_magic_item(a["mode"], a["item"]) }),

      ToolSpec.new(name: "shop", description: "Buy, sell, list, value, or offer in a shop.",
                   properties: {
                     "op"   => enum(P::SHOP_OPS, description: "Shop operation."),
                     "args" => str("Optional argument (item name, etc.).")
                   },
                   required: ["op"],
                   builder: ->(a) {
                     args = present?(a["args"]) ? a["args"] : nil
                     P.shop(a["op"], args: args)
                   }),

      ToolSpec.new(name: "practice", description: "Practice a skill, or list what you can practice.",
                   properties: { "skill" => str("Optional skill to practice.") },
                   required: [],
                   builder: ->(a) {
                     skill = present?(a["skill"]) ? a["skill"] : nil
                     P.practice(skill)
                   }),

      ToolSpec.new(name: "save_character", description: "Save your character to disk.",
                   builder: ->(_a) { P.save_char }),

      ToolSpec.new(name: "send_raw", description: "Send a raw command line to the MUD (escape hatch).",
                   properties: { "raw" => str("The raw command text.") },
                   required: ["raw"],
                   builder: ->(a) { a["raw"] }),

      ToolSpec.new(name: "poll", description: "Return any async output that arrived since the last command.",
                   builder: ->(_a) { nil }),

      ToolSpec.new(name: "mud_status", description: "Report the current connection and login status.",
                   builder: ->(_a) { nil })
    ].freeze

    def self.tools
      TOOLS
    end

    def self.find(name)
      TOOLS.find { |t| t.name == name.to_s }
    end

    # Serialize the tool surface as the language-neutral primitives.json spec.
    def self.to_json_spec
      JSON.pretty_generate(
        "name"    => "mud-manager",
        "version" => MudManagerMcp::VERSION,
        "tools"   => TOOLS.map(&:to_mcp_tool)
      )
    end
  end
end
