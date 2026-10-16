from collections import deque
import heapq
import json
import os

from hospital import (
    hospitals,
    load_hospitals,
    find_hospitals_by_specialzation,
    calculate_hospital_score,
    add_hospital,
    edit_hospital,
    remove_hospital,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROADS_FILE = os.path.join(BASE_DIR, "data", "roads.json")


class Graph:
    def __init__(self):
        self.graph = {}

    def clone(self):
        new_g = Graph()
        for loc, edges in self.graph.items():
            new_g.graph[loc] = list(edges)
        return new_g

    def add_location(self, location):
        if location not in self.graph:
            self.graph[location] = []

    def add_road(self, source, destination, distance):
        self.add_location(source)
        self.add_location(destination)
        self.graph[source].append((destination, distance))
        self.graph[destination].append((source, distance))

    def get_neighbors(self, location):
        return self.graph.get(location, [])

    def remove_road(self, source, destination):
        if source not in self.graph or destination not in self.graph:
            return False

        a = None
        for road in self.graph[source]:
            if road[0] == destination:
                a = road[1]
                break

        if a is None:
            return False

        self.graph[source].remove((destination, a))
        self.graph[destination].remove((source, a))
        return True

    def update_road(self, source, destination, new_distance):
        if not self.remove_road(source, destination):
            return False

        self.add_road(source, destination, new_distance)
        return True

    def road_exists(self, source, destination):
        if source not in self.graph:
            return False

        for road in self.graph[source]:
            if road[0] == destination:
                return True

        return False

    def bfs(self, source, destination):
        if source not in self.graph:
            return
        visited = set()
        queue = deque()
        queue.append(source)
        visited.add(source)
        while queue:
            current = queue.popleft()
            print(current)
            if current == destination:
                break
            for roads in self.graph[current]:
                neighbour = roads[0]
                if neighbour not in visited:
                    queue.append(neighbour)
                    visited.add(neighbour)

    def dfs(self, source, destination):
        if source not in self.graph:
            return
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
                neighbour = roads[0]
                if neighbour not in visited:
                    stack.append(neighbour)
                    visited.add(neighbour)

    def dijkstra(self, source, destination):
        if source not in self.graph or destination not in self.graph:
            return [], float("inf")

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
                    heapq.heappush(priority_queue, (new_distance, neighbour))

        if distances[destination] == float("inf"):
            return [], float("inf")

        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path, distances[destination]


def update_rdata(graph=None):
    target_graph = graph if graph is not None else g
    roads = []
    seen = set()

    for source in target_graph.graph:
        for road in target_graph.graph[source]:
            destination = road[0]
            distance = road[1]

            road_pair = tuple(sorted([source, destination]))

            if road_pair in seen:
                continue

            seen.add(road_pair)

            roads.append({
                "source": source,
                "destination": destination,
                "distance": distance
            })
    with open(ROADS_FILE, "w") as file:
        json.dump(roads, file, indent=4)


def load_graph():
    graph = Graph()
    if os.path.exists(ROADS_FILE):
        with open(ROADS_FILE, "r") as file:
            roads = json.load(file)
        for road in roads:
            graph.add_road(road["source"], road["destination"], road["distance"])
    return graph


g = load_graph()


def simulate_incident(graph, source_node, destination_node, incident_type, traffic_delay=0):
    """
    Creates an in-memory clone of the given graph with a simulated road incident.
    Operates strictly in memory; does NOT modify or persist to data/roads.json.
    
    incident_type: 'closure' or 'traffic'
    """
    sim_g = graph.clone()
    if incident_type == "closure":
        sim_g.remove_road(source_node, destination_node)
    elif incident_type == "traffic":
        current_dist = None
        for neighbor, dist in sim_g.get_neighbors(source_node):
            if neighbor == destination_node:
                current_dist = dist
                break
        if current_dist is not None:
            sim_g.update_road(source_node, destination_node, current_dist + traffic_delay)
    return sim_g


def rank_hospitals(g, source, emergency):
    """
    Evaluates and ranks all eligible hospitals for an emergency based on:
    1. Specialization match
    2. Available beds (> 0) and ICU capacity (> 0)
    3. Route reachability and shortest distance via Dijkstra algorithm
    4. Composite suitability score balancing capacity and transit cost
    
    Formula:
        Score = (Beds + 2 * ICU) / (Route Distance + 1)
        
    Returns a sorted list of dictionaries with ranking details.
    """
    if source not in g.graph:
        return []

    suitable = find_hospitals_by_specialzation(emergency)
    eligible_hospitals = []

    for name in suitable:
        details = hospitals.get(name, {})
        loc = details.get("location")
        beds = details.get("beds", 0)
        icu = details.get("icu", 0)

        # Validate location in graph and available capacity
        if not loc or loc not in g.graph or beds <= 0 or icu <= 0:
            continue

        path, dist = g.dijkstra(source, loc)

        # Hospital must be reachable
        if dist == float("inf") or not path:
            continue

        score = calculate_hospital_score(beds, icu, dist)
        eligible_hospitals.append({
            "name": name,
            "location": loc,
            "distance": dist,
            "path": path,
            "beds": beds,
            "icu": icu,
            "specializations": details.get("specializations", []),
            "score": score,
        })

    # Sort primarily by composite score descending; break ties by distance ascending
    eligible_hospitals.sort(key=lambda h: (-h["score"], h["distance"]))

    # Generate transparent explanations for each ranked option
    for rank, h in enumerate(eligible_hospitals, start=1):
        h["rank"] = rank
        if rank == 1:
            h["explanation"] = (
                f"Top recommendation (Score: {h['score']:.2f}). Selected for {emergency} with "
                f"{h['beds']} beds and {h['icu']} ICU units across {h['distance']} distance units from Node {source}. "
                f"Achieves the optimal balance of critical capacity and route proximity."
            )
        else:
            h["explanation"] = (
                f"Ranked #{rank} (Score: {h['score']:.2f}). Transit distance: {h['distance']} units, "
                f"Capacity: {h['beds']} beds, {h['icu']} ICU. Lower overall capacity-to-distance ratio."
            )

    return eligible_hospitals


def find_hospital(g, source, emergency):
    """
    Finds the recommended hospital using smart capacity and proximity ranking.
    Preserves backward compatibility: returns (hospital_name, path, distance).
    """
    ranked = rank_hospitals(g, source, emergency)
    if not ranked:
        return "No hospital found", [], float("inf")
    top = ranked[0]
    return top["name"], top["path"], top["distance"]


def main():
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

                source = input("Enter your location: ").strip().upper()
                if source not in g.graph:
                    print("Location not found")
                    continue
                emergency = input("Enter emergency type: ").strip().title()

                ranked = rank_hospitals(g, source, emergency)

                if not ranked:
                    print("No suitable hospital or route found")
                else:
                    top = ranked[0]
                    print(f"\nTop Recommended Hospital: {top['name']}")
                    print(f"Location: Node {top['location']}")
                    print(f"Route: {' -> '.join(top['path'])}")
                    print(f"Distance: {top['distance']}")
                    print(f"Capacity: {top['beds']} beds, {top['icu']} ICU")
                    print(f"Composite Score: {top['score']}")
                    print(f"Explanation: {top['explanation']}")

                    if len(ranked) > 1:
                        print("\nOther eligible facilities:")
                        for h in ranked[1:]:
                            print(
                                f"  #{h['rank']} {h['name']} (Node {h['location']}) | "
                                f"Dist: {h['distance']} | Beds: {h['beds']} | ICU: {h['icu']} | "
                                f"Score: {h['score']}"
                            )

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
                        update_rdata()
                        print("Road added")

                    case "2":
                        source = input("Enter source: ")
                        destination = input("Enter destination: ")
                        if source not in g.graph or destination not in g.graph:
                            print("Location not found")
                            continue
                        distance = int(input("Enter new distance: "))

                        g.update_road(source, destination, distance)
                        update_rdata()
                        print("Traffic updated")

                    case "3":
                        source = input("Enter source: ")
                        destination = input("Enter destination: ")
                        if source not in g.graph or destination not in g.graph:
                            print("Location not found")
                            continue
                        if g.remove_road(source, destination):
                            update_rdata()
                            print("Road closed")
                        else:
                            print("Road not found")

                    case "4":
                        source = input("Enter source: ")
                        destination = input("Enter destination: ")

                        if source not in g.graph or destination not in g.graph:
                            print("Location not found")
                            continue

                        if g.road_exists(source, destination):
                            print("Road is already open")
                            continue

                        distance = int(input("Enter distance: "))
                        g.add_road(source, destination, distance)
                        update_rdata()
                        print("Road opened")

                    case "5":
                        continue

            case "4":
                print("Exiting SmartRoute...")
                break

            case _:
                print("Invalid choice")


if __name__ == "__main__":
    main()