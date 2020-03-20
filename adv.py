from room import Room
from player import Player
from world import World
from util import Queue

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
# Reverse function used to express bidirectional relationships between vertices
def reverse(direction):
    if direction == 'n':
        return 's'
    elif direction == 's':
        return 'n'
    elif direction == 'e':
        return 'w'
    elif direction == 'w':
        return 'e'
    else:
        return 'Cannot reverse that direction'

def adv_dft(graph, player, traversal_path, current_room):
    # Shuffles the exits of current room and goes in a random direction as deep as possible until a dead end is hit
    directions = list(graph[current_room].keys())
    random.shuffle(directions)
    # Loop through exits until unexplored is found
    for direction in directions:
        # If unexplored exit: travel in that direction, add it to the traversal path and get the new room
        if graph[current_room][direction] == '?':
            player.travel(direction)
            traversal_path.append(direction)
            new_room = player.current_room.id
            # If the new room isn't in graph: initialize it with unexplored exit
            if new_room not in graph:
                graph[new_room] = {}
                for move in player.current_room.get_exits():
                    graph[new_room][move] = '?'
            # Update graph to reflect connections of rooms. Update current room to be the new room for the next loop and then break out of the loop.
            graph[current_room][direction] = new_room
            graph[new_room][reverse(direction)] = current_room
            current_room = new_room
            break
    if '?' in graph[current_room].values():
        adv_dft(graph, player, traversal_path, current_room)

def adv_bfs(graph, current_room):
    # Create a queue
    q = Queue()
    # Enqueue the current room
    q.enqueue([current_room])
    # Create a set to store visited vertices
    visited = set()
    # While the queue is not empty...
    while q.size() > 0:
        # Dequeue the first path
        path = q.dequeue()
        # Grab the room from the end of the path
        room = path[-1]
        if room not in visited:
            visited.add(room)
            # If there is an '?' in the room's exit: go to that room
            for direction in graph[room]:
                if graph[room][direction] == '?':
                    return path
                new_path = list(path)
                new_path.append(graph[room][direction])
                q.enqueue(new_path)

### DFT to dead-end then BFS to the nearest room with an unexplored exit ###

graph = {}
# Loop until the graph has the same length as number of rooms then get the current room player is in
while len(graph) < len(world.rooms):
    current_room = player.current_room.id
    # If that room isn't in graph, initialize it with '?' for all directions
    if current_room not in graph:
        graph[current_room] = {}
        for direction in player.current_room.get_exits():
            graph[current_room][direction] = '?'
    # DFT to get to dead-end
    adv_dft(graph, player, traversal_path, current_room)
    # Find the path to closest room with an unexplored exit
    path = adv_bfs(graph, current_room)
    # If there is no path, we have visited every room
    if path:
        # Move player along the path to get back to the room with an unexplored exit then check directions to see where to go next. Append the direction to the traversal path, move the player and set current room.
        for room in path:
            for direction in graph[current_room]:
                if graph[current_room][direction] == room:
                    traversal_path.append(direction)
                    player.travel(direction)
            current_room = player.current_room.id

# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")

sims = open('simulations.txt', 'a')
sims.write(f'{len(traversal_path)}\n')
sims.close()


#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
