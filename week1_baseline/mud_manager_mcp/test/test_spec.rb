# frozen_string_literal: true

require_relative "helper"

class TestSpec < Minitest::Test
  def test_exposes_26_tools
    assert_equal 26, MudManagerMcp::Spec.tools.size
  end

  def test_expected_tool_names_are_present
    names = MudManagerMcp::Spec.tools.map(&:name)
    %w[look move attack cast_spell poll mud_status send_raw].each do |n|
      assert_includes names, n
    end
  end

  def test_move_schema_carries_the_direction_enum
    move = MudManagerMcp::Spec.find("move")
    assert_equal MudManager::Primitives::DIRECTIONS, move.properties["direction"]["enum"]
    assert_equal ["direction"], move.required
  end

  def test_attack_defaults_style_to_kill
    spec = MudManagerMcp::Spec.find("attack")
    assert_equal "kill dragon", spec.build("target" => "dragon").raw
    assert_equal "murder orc", spec.build("style" => "murder", "target" => "orc").raw
  end

  def test_move_rejects_an_unknown_direction
    err = assert_raises(ArgumentError) do
      MudManagerMcp::Spec.find("move").build("direction" => "sideways")
    end
    assert_match(/invalid direction/, err.message)
  end

  def test_cast_spell_requires_a_spell
    err = assert_raises(ArgumentError) do
      MudManagerMcp::Spec.find("cast_spell").build("spell" => "")
    end
    assert_match(/required/, err.message)
  end

  def test_spec_serializes_to_json
    json = MudManagerMcp::Spec.to_json_spec
    parsed = JSON.parse(json)
    assert_equal "mud-manager", parsed["name"]
    assert_equal 26, parsed["tools"].size
  end
end
