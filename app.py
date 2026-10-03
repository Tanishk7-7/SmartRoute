from collections import deque
from hospital import hospitals , find_hospitals_by_specialzation, add_hospital, edit_hospital, remove_hospital
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
        self.remove_road(source,destination)
        self.add_road(source,destination,new_distance)

        self.remove_road(destination,source)
        self.add_road(destination,source,new_distance)

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

def find_hospital(g,source , emergency):
    suitable = find_hospitals_by_specialzation(emergency)
    closest = float("inf")
    name1 = "No hospital found"
    path1 = []
    for name in suitable:
        loc = hospitals[name]["location"]
        path , dist = g.dijkstra(source,loc)
        if dist < closest:
            closest = dist
            name1 = name
            path1 = path
    return name1 , path1, closest


g.add_location("A")
g.add_road("A", "B", 5)
g.add_road("A", "E", 4)
g.add_road("B", "C", 6)
g.add_road("B", "F", 3)
g.add_road("C", "D", 4)
g.add_road("E", "F", 5)
g.add_road("F", "G", 4)
g.add_road("F", "I", 6)
g.add_road("G", "H", 5)
g.add_road("H", "J", 3)
g.add_road("G", "C", 3)
g.add_road("I", "J", 4)
g.add_road("D", "H", 6)


while True:

    print("\n===== SmartRoute =====")
    print("1. Find Hospital")
    print("2. Hospital Management")
    print("3. Road Management")
    print("4. Exit")

    choice = input("Enter choice: ")

    match choice:

        case "1":
            print("\n--- Find Hospital ---")

            source = input("Enter your location: ")
            emergency = input("Enter emergency type: ").title()

            name, path, dist = find_hospital(g, source, emergency)

            if dist == float("inf"):
                print("No suitable hospital or route found")
            else:
                print("Hospital:", name)
                print("Route:", " -> ".join(path))
                print("Distance:", dist)

        case "2":
            print("\n--- Hospital Management ---")
            print("1. Add Hospital")
            print("2. Edit Hospital")
            print("3. Remove Hospital")
            print("4. Back")

            choice = input("Enter choice: ")

            match choice:
                case "1":
                    
                    name = input("Enter hospital name: ")
                    location = input("Enter location: ")
                    specializations = input("Enter specializations: ").split(",")
                    beds = int(input("Enter beds: "))
                    icu = int(input("Enter ICU beds: "))

                    add_hospital(name, location, specializations, beds, icu)

                    print("Hospital added")

                case "2":
                        name = input("Enter hospital name: ")
                        location = input("Enter new location: ")
                        specializations = input("Enter specializations: ").split(",")
                        beds = int(input("Enter beds: "))
                        icu = int(input("Enter ICU beds: "))

                        edit_hospital(name, location, specializations, beds, icu)

                        print("Hospital updated")

                case "3":
                       name = input("Enter hospital name: ")
                       remove_hospital(name)
                       print("Hospital removed")

                case "4":
                    continue

        case "3":
            print("\n--- Road Management ---")
            print("1. Add Road")
            print("2. Update Traffic")
            print("3. Close Road")
            print("4. Open Road")
            print("5. Back")

            choice = input("Enter choice: ")

            match choice:
                case "1":
                    source = input("Enter source: ")
                    destination = input("Enter destination: ")
                    distance = int(input("Enter distance: "))

                    g.add_road(source, destination, distance)

                    print("Road added")

                case "2":
                    source = input("Enter source: ")
                    destination = input("Enter destination: ")
                    distance = int(input("Enter new distance: "))

                    g.update_road(source, destination, distance)

                    print("Traffic updated")

                case "3":
                    source = input("Enter source: ")
                    destination = input("Enter destination: ")

                    g.remove_road(source, destination)

                    print("Road closed")

                case "4":
                    source = input("Enter source: ")
                    destination = input("Enter destination: ")
                    distance = int(input("Enter distance: "))

                    g.add_road(source, destination, distance)

                    print("Road opened")

                case "5":
                    continue

        case "4":
            print("Exiting SmartRoute...")
            break

        case _:
            print("Invalid choice")