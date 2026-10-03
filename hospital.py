hospitals = {
    "City Care": {
        "location": "B",
        "specializations": ["Cardiology", "Emergency"],
        "beds": 10,
        "icu": 3
    },

    "Metro Hospital": {
        "location": "C",
        "specializations": ["Trauma", "Emergency"],
        "beds": 15,
        "icu": 4
    },

    "LifeLine Hospital": {
        "location": "D",
        "specializations": ["Cardiology", "Trauma"],
        "beds": 12,
        "icu": 5
    },

    "Green Valley": {
        "location": "E",
        "specializations": ["Emergency", "Neurology"],
        "beds": 8,
        "icu": 2
    },

    "Sunrise Hospital": {
        "location": "F",
        "specializations": ["Cardiology", "Neurology"],
        "beds": 20,
        "icu": 6
    },

    "Apollo Care": {
        "location": "G",
        "specializations": ["Trauma", "Emergency"],
        "beds": 14,
        "icu": 3
    },

    "City General": {
        "location": "H",
        "specializations": ["Emergency", "Cardiology", "Trauma"],
        "beds": 25,
        "icu": 8
    },

    "Hope Hospital": {
        "location": "I",
        "specializations": ["Neurology", "Emergency"],
        "beds": 9,
        "icu": 2
    }
}
def find_hospitals_by_specialzation(emergency_type):
    suitable = []
    for name , details in hospitals.items():
        if emergency_type in details["specializations"] and details["icu"]>0 and details["beds"]>0:
            suitable.append(name)
    
    return suitable
def add_hospital(name, location, specializations, beds, icu):
    hospitals[name] = {
        "location": location,
        "specializations": specializations,
        "beds": beds,
        "icu": icu
    }
def edit_hospital(name, location, specializations, beds, icu):
    hospitals[name]["location"] = location
    hospitals[name]["specializations"] = specializations
    hospitals[name]["beds"] = beds
    hospitals[name]["icu"] = icu

def remove_hospital(name):
    del hospitals[name]
