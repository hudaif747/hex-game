class HexValue:
    computer = "computer"
    player = "player"
    undefined = "undefined"


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Path:
    def __init__(self, from_hex, to_hex, path_hexes, distance):
        self.from_hex = from_hex
        self.to_hex = to_hex
        self.path_hexes = path_hexes
        self.distance = distance


class Hex:
    def __init__(self, position, value, board=None, outside=False):
        self.position = position
        self.value = value
        self.board = board
        self.outside = outside
        self.path_length_from_start = float('inf')
        self.path_vertices_from_start = []

    def clear_vertex_cache(self):
        self.path_length_from_start = float('inf')
        self.path_vertices_from_start = []

    @property
    def neighbors(self):
        if self.board is None:
            return []
        return list(set(self.board.get_neighbors_for(self)))


class Graph:
    def __init__(self, hexes):
        self.vertices = set(hexes)

    def get_shortest_path_from(self, hex_obj, destination_hex, perspective):
        if hex_obj.value == perspective:
            self.find_shortest_paths_using_dijkstra(hex_obj, perspective)
            path = Path(hex_obj, destination_hex, destination_hex.path_vertices_from_start, destination_hex.path_length_from_start)
            return path
        return None

    def find_shortest_paths_using_dijkstra(self, start_vertex, perspective):
        for vertex in self.vertices:
            vertex.clear_vertex_cache()

        current_vertices = set(self.vertices)
        start_vertex.path_length_from_start = 0
        start_vertex.path_vertices_from_start.append(start_vertex)

        current_vertex = start_vertex

        while current_vertex:
            current_vertices.remove(current_vertex)
            not_checked_neighbors = [neighbor for neighbor in current_vertex.neighbors if neighbor in current_vertices]
            filtered_neighbors = [neighbor for neighbor in not_checked_neighbors if neighbor.value == HexValue.undefined or neighbor.value == perspective]

            for neighbor_vertex in filtered_neighbors:
                weight = 0.0 if neighbor_vertex.value == perspective else 1.0
                theoretic_new_weight = current_vertex.path_length_from_start + weight

                if theoretic_new_weight < neighbor_vertex.path_length_from_start:
                    neighbor_vertex.path_length_from_start = theoretic_new_weight
                    neighbor_vertex.path_vertices_from_start = list(current_vertex.path_vertices_from_start)
                    neighbor_vertex.path_vertices_from_start.append(neighbor_vertex)

            if not current_vertices:
                return
            else:
                current_vertex = min(current_vertices, key=lambda vertex: vertex.path_length_from_start)


def get_player_shortest_path(graph, outside_left_hex_position, outside_right_hex_position):
    graph_instance = Graph()

    hex_graph = graph_instance if graph_instance else None
    from_hex = get_hex_for_position(outside_left_hex_position) if outside_left_hex_position else None
    to_hex = get_hex_for_position(outside_right_hex_position) if outside_right_hex_position else None

    if hex_graph and from_hex and to_hex:
        return hex_graph.get_shortest_path_from(from_hex, to_hex, perspective="player")

    return None


def get_computer_shortest_path(graph, outside_down_hex_position, outside_top_hex_position):
    graph_instance = Graph()

    hex_graph = graph_instance if graph_instance else None
    from_hex = get_hex_for_position(outside_down_hex_position) if outside_down_hex_position else None
    to_hex = get_hex_for_position(outside_top_hex_position) if outside_top_hex_position else None

    if hex_graph and from_hex and to_hex:
        return hex_graph.get_shortest_path_from(from_hex, to_hex, perspective="computer")

    return None


def get_neighbor_positions(position, hexes, outside_left_hex_position, outside_right_hex_position,
                            outside_top_hex_position, outside_down_hex_position):
    if position == outside_left_hex_position:
        return [hex_obj.position for hex_obj in hexes if hex_obj.position.x == 0]
    elif position == outside_right_hex_position:
        return [hex_obj.position for hex_obj in hexes if hex_obj.position.x == 5]
    elif position == outside_top_hex_position:
        return [hex_obj.position for hex_obj in hexes if hex_obj.position.y == 5]
    elif position == outside_down_hex_position:
        return [hex_obj.position for hex_obj in hexes if hex_obj.position.y == 0 and hex_obj.position.x <= 5]
    else:
        positions = [
            Position(position.x, position.y + 1),
            Position(position.x + 1, position.y),
            Position(position.x + 1, position.y - 1),
            Position(position.x, position.y - 1),
            Position(position.x - 1, position.y),
            Position(position.x - 1, position.y + 1),
        ]

        if position.x == 0:
            positions.append(outside_left_hex_position)
        if position.x == 5:
            positions.append(outside_right_hex_position)
        if position.y == 5:
            positions.append(outside_top_hex_position)
        if position.y == 0 and position.x <= 5:
            positions.append(outside_down_hex_position)

        return positions


def get_score_for_path(path, value):
    if path and path.distance == 0.0:
        return float('-inf')  # Game over
    else:
        return float(len([hex_value for hex_value in path.path_hexes if hex_value == HexValue.undefined]))

# Till here
def get_heuristic_score():
    def get_computer_shortest_path():
        # Implement the logic to get the computer's shortest path
        pass

    def get_player_shortest_path():
        # Implement the logic to get the player's shortest path
        pass

    computer_path = get_computer_shortest_path()
    player_path = get_player_shortest_path()

    computer_score = get_score_for_path(computer_path, HexValue.computer)
    player_score = get_score_for_path(player_path, HexValue.player)

    return player_score - computer_score
