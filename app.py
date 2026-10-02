from collections import deque
import heapq
class Graph:
    def __init__(self):
        self.graph= {}
    def add_location(self, location):
        if location not in self.graph:
            self.graph[location]=[]
    

    def add_road(self,source , destination,distance):
        self.add_location(source)
        self.add_location(destination)
        self.graph[source].append((destination,distance))
        self.graph[destination].append((source,distance))

    def get_neighbors(self, location):
     return self.graph.get(location, [])
    
    def remove_road(self , source , destination):
        for road in self.graph[source]:
            if road[0]== destination:
                a = road[1]
        self.graph[source].remove((destination,a))
        self.graph[destination].remove((source,a))

    def update_road(self , source , destination , new_distance):
        for road in self.graph[source]:
            self.graph[source].remove(road)
            self.graph[source].append((destination, new_distance))
            break

        for road in self.graph[destination]:
            self.graph[destination].remove(road)
            self.graph[destination].append((source, new_distance))
            break

    def bfs(self, source, destination):
        visited = set()
        queue = deque()
        queue.append(source)
        visited.add(source)
        while queue:
            current = queue.popleft()
            print(current)
            if current == destination :
                break
            for roads in self.graph[current]:
                neighbour = roads[0]
                if neighbour not in visited:
                    queue.append(neighbour)
                    visited.add(neighbour)

    def dfs(self, source, destination):
        visited = set()
        stack = []
        stack.append(source)
        visited.add(source)
        while stack:
            current = stack.pop()
            print(current)
            if current == destination:
                break
            for roads in self.graph[current]:
                neighnour = roads[0]
                if neighnour not in visited:
                    stack.append(neighnour)
                    visited.add(neighnour)


    def dijkstra(self, source, destination):

        distances = {}
        previous = {}

        for location in self.graph:
            distances[location] = float("inf")
            previous[location] = None

        distances[source] = 0

        priority_queue = []
        heapq.heappush(priority_queue, (0, source))

        visited = set()

        while priority_queue:

            current_distance, current = heapq.heappop(priority_queue)

            if current in visited:
                continue

            visited.add(current)

            if current == destination:
                break

            for road in self.graph[current]:

                neighbour = road[0]
                road_distance = road[1]

                new_distance = current_distance + road_distance

                if new_distance < distances[neighbour]:

                    distances[neighbour] = new_distance
                    previous[neighbour] = current

                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbour)
                    )
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current=previous[current]
        path.reverse()
        return path , distances[destination]


g = Graph()

g.add_location("A")

g.add_road("A", "B", 5)
g.add_road("A", "C", 3)
g.add_road("B", "D", 4)
g.add_road("C", "D", 2)

print(g.graph)

print(g.get_neighbors("A"))
print(g.get_neighbors("B"))
#g.remove_road("C","D")
#print("Road from A to B is closed then")
print(g.get_neighbors("A"))
print(g.get_neighbors("B"))

g.bfs("D","C")
print("DFS traversal:")
g.dfs("A", "D")

heap = []

heapq.heappush(heap, (5, "A"))
heapq.heappush(heap, (2, "B"))
heapq.heappush(heap, (8, "C"))
heapq.heappush(heap, (1, "D"))

print(heap)

print(heapq.heappop(heap))
print(heapq.heappop(heap))
print(heapq.heappop(heap))
print(heapq.heappop(heap))

g.update_road("C", "D", 20)

print("Shortest distance:")
path, distance = g.dijkstra("A", "D")

print(path)
print(distance)