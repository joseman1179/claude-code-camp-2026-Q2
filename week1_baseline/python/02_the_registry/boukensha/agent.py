from __future__ import annotations


class Agent:
    """BFS pathfinding agent that navigates from a start room to the bakery (room 3009)."""

    DIR_MAP: dict[int, str] = {
        0: "north",
        1: "east",
        2: "south",
        3: "west",
        4: "up",
        5: "down",
    }

    def __init__(
        self,
        start_room: int,
        rooms_data: dict,
        shop_data: dict,
        objects_data: dict,
    ) -> None:
        self.current_room: int = start_room
        self.rooms_data: dict = rooms_data
        self.shop_data: dict = shop_data
        self.objects_data: dict = objects_data
        self.target_room: int = 3009  # The Bakery
        self.path: list[tuple[int, int]] | None = self._calculate_path(
            start_room, self.target_room
        )

    def cognize(self) -> str:
        if self.current_room != self.target_room:
            if self.path:
                step = self.path.pop(0)
                direction, next_room = step
                self.current_room = next_room
                return f"move {self.DIR_MAP[direction]}"
            else:
                return "stand"
        else:
            return "list"

    # ---------- private ---------------------------------------------------

    def _calculate_path(
        self, start_room: int, target_room: int
    ) -> list[tuple[int, int]] | None:
        queue: list[tuple[int, list[tuple[int, int]]]] = [(start_room, [])]
        visited: dict[int, bool] = {start_room: True}

        while queue:
            current_room, path = queue.pop(0)

            if current_room == target_room:
                return path

            room_data = self.rooms_data.get(str(current_room))
            if not room_data or "exits" not in room_data:
                continue

            for exit_data in room_data["exits"]:
                neighbor = exit_data["room_linked"]
                direction = exit_data["dir"]

                if neighbor not in visited:
                    visited[neighbor] = True
                    queue.append((neighbor, path + [(direction, neighbor)]))

        return None
