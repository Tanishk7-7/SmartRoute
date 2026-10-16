import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOSPITALS_FILE = os.path.join(BASE_DIR, "data", "hospitals.json")

def load_hospitals():
    global hospitals
    with open(HOSPITALS_FILE, "r") as file:
        hospitals = json.load(file)
    return hospitals

with open(HOSPITALS_FILE, "r") as file:
    hospitals = json.load(file)

def save_hospitals():
    with open(HOSPITALS_FILE, "w") as file:
        json.dump(hospitals, file, indent=4)

def find_hospitals_by_specialzation(emergency_type):
    suitable = []
    target = emergency_type.strip().lower() if isinstance(emergency_type, str) else str(emergency_type).lower()
    for name, details in hospitals.items():
        specs = [s.strip().lower() for s in details.get("specializations", [])]
        if target in specs and details.get("icu", 0) > 0 and details.get("beds", 0) > 0:
            suitable.append(name)
    
    return suitable

def calculate_hospital_score(beds, icu, distance):
    """
    Transparent, beginner-friendly heuristic scoring formula:
    Score = (Available Beds + 2 * ICU Beds) / (Route Distance + 1)
    
    - Capacity Weighting: ICU beds are weighted 2x due to critical care priority.
    - Proximity Penalty: Route distance in the denominator penalizes distant facilities.
    - Zero Division Avoidance: Adding 1 to distance handles origin at hospital node (distance 0).
    Note: Heuristic for educational/simulation prototype; not clinically validated.
    """
    if distance == float("inf") or distance < 0:
        return 0.0
    if beds <= 0 or icu <= 0:
        return 0.0
    weighted_capacity = float(beds) + (2.0 * float(icu))
    score = weighted_capacity / (float(distance) + 1.0)
    return round(score, 2)


def add_hospital(name, location, specializations, beds, icu):
    hospitals[name] = {
        "location": location,
        "specializations": specializations,
        "beds": beds,
        "icu": icu
    }
    save_hospitals()

def edit_hospital(name, location, specializations, beds, icu):
    hospitals[name]["location"] = location
    hospitals[name]["specializations"] = specializations
    hospitals[name]["beds"] = beds
    hospitals[name]["icu"] = icu
    save_hospitals()

def remove_hospital(name):
    del hospitals[name]
    save_hospitals()

