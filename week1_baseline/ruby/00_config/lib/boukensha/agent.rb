module Boukensha
  class Agent
    def initialize(start_room, rooms_data, shop_data, objects_data)
      @current_room = start_room
      @rooms_data = rooms_data
      @shop_data = shop_data
      @objects_data = objects_data
      @target_room = 3009 # The Bakery
      @path = calculate_path(start_room, @target_room)
    end

    def cognize
      if @current_room != @target_room
        if @path && !@path.empty?
          step = @path.shift
          direction, next_room = step
          @current_room = next_room
          dir_map = {0 => 'north', 1 => 'east', 2 => 'south', 3 => 'west', 4 => 'up', 5 => 'down'}
          return "move #{dir_map[direction]}"
        else
          return "stand"
        end
      else
        return "list"
      end
    end

    private

    def calculate_path(start_room, target_room)
      queue = [[start_room, []]]
      visited = {start_room => true}

      while !queue.empty?
        current_room, path = queue.shift
        
        if current_room == target_room
          return path
        end

        room_data = @rooms_data[current_room.to_s]
        next unless room_data && room_data['exits']

        room_data['exits'].each do |exit_data|
          neighbor = exit_data['room_linked']
          direction = exit_data['dir']
          
          if !visited[neighbor]
            visited[neighbor] = true
            queue.push([neighbor, path + [[direction, neighbor]]])
          end
        end
      end
      nil
    end
  end
end
